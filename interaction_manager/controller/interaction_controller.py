#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# DATABASE_CONTROLLER #
# =========================== #
# Class for managing the interaction flow with the robot.
#
# @author ES
# **

import logging
import time

from es_common.utils.qt import QTimer

from block_manager.enums.block_enums import ExecutionMode
from es_common.enums.command_enums import ActionCommand
from es_common.factory.module_factory import ModuleFactory
from es_common.model.observable import Observable
from es_common.utils.timer_helper import TimerHelper
from interaction_manager.utils import config_helper
from robot_manager.pepper.controller.robot_controller import RobotController
from thread_manager.robot_animation_threads import AnimateRobotThread
from thread_manager.robot_connection_thread import RobotConnectionThread
from thread_manager.robot_engagement_thread import RobotEngagementThread
from thread_manager.robot_face_detection_thread import RobotFaceDetectionThread
from thread_manager.wakeup_robot_thread import WakeUpRobotThread


class InteractionController(object):
    def __init__(self, block_controller, music_controller=None):
        self.logger = logging.getLogger("Interaction Controller")

        self.block_controller = block_controller
        self.music_controller = music_controller
        self.robot_controller = None
        self.wakeup_thread = None
        self.animation_thread = None
        self.engagement_thread = None
        self.face_detection_thread = None
        self.connection_thread = None
        self.timer_helper = TimerHelper()
        self.music_command = None
        self.animations_lst = []
        self.animation_time = 0
        self.animation_counter = -1
        self.robot_volume = 50

        self.robot_name = None
        self.robot_realm = None

        self.engagement_counter = 0
        self.is_ready_to_interact = False
        self.current_interaction_block = None
        self.previous_interaction_block = None
        self.interaction_blocks = None
        self.interaction_design = None
        self.interaction_module = None

        self.stop_playing = False
        self.execution_result = None
        self.has_finished_playing_observers = Observable()
        self.threads = []
        self.on_connected_observers = Observable()

    def connect_to_robot(self, robot_name=None, robot_realm=None):
        self.robot_name = robot_name
        self.robot_realm = robot_realm

        self.connection_thread = RobotConnectionThread()
        self.connection_thread.connect_to_robot(session_observer=self.on_connected,
                                                robot_name=robot_name, robot_realm=robot_realm)

    def on_connected(self, session):
        self.logger.debug("Received session: {}".format(session))
        self.robot_controller = RobotController()  # self.connection_thread.robot_controller
        self.robot_controller.set_session(session=session)
        self.update_threads()
        self.on_connected_observers.notify_all(True)

    def disconnect_from_robot(self):
        self.engagement_counter = 0
        try:
            self.stop_all_threads()
            self.logger.info("Disconnecting in 10s...")
            time.sleep(1)
            self.robot_controller = None
        except Exception as e:
            self.logger.error("Error while disconnecting from robot. | {}".format(e))

        return True

    def stop_all_threads(self):
        # close all threads
        for thread in self.threads:
            try:
                thread.stop_running()
                thread.quit()
                thread.wait()
            except Exception as e:
                self.logger.error("Error while stopping thread: {} | {}".format(thread, e))
                continue
        self.threads = []

    def is_connected(self):
        return False if self.robot_controller is None else True

    def update_threads(self):
        self.threads = []

        self.animation_thread = AnimateRobotThread(robot_controller=self.robot_controller)
        self.animation_thread.customized_say_completed_observers.add_observer(self.customized_say)
        self.animation_thread.animate_completed_observers.add_observer(self.on_animation_completed)
        self.animation_thread.is_disconnected.connect(self.disconnect_from_robot)

        self.threads.append(self.animation_thread)

        self.face_detection_thread = RobotFaceDetectionThread(robot_controller=self.robot_controller)
        self.face_detection_thread.is_disconnected.connect(self.disconnect_from_robot)

        self.threads.append(self.face_detection_thread)

        self.engagement_thread = RobotEngagementThread(robot_controller=self.robot_controller)
        self.engagement_thread.is_disconnected.connect(self.disconnect_from_robot)
        self.robot_controller.is_engaged_observers.add_observer(self.interaction)

        self.threads.append(self.engagement_thread)

    def update_detection_certainty(self, speech_certainty=None, face_certainty=None):
        if self.robot_controller is not None:
            self.robot_controller.update_detection_certainty(speech_certainty=speech_certainty,
                                                             face_certainty=face_certainty)

    def update_delay_between_blocks(self, delay=None):
        if self.robot_controller is not None:
            self.robot_controller.update_delay_between_blocks(delay=delay)

    def wakeup_robot(self):
        success = False
        try:
            if self.wakeup_thread is None:
                self.wakeup_thread = WakeUpRobotThread(robot_controller=self.robot_controller)
                self.threads.append(self.wakeup_thread)

            self.wakeup_thread.stand()

            success = True
        except Exception as e:
            self.logger.error("Error while waking up the robot! | {}".format(e))
        finally:
            return success

    def rest_robot(self):
        try:
            if self.wakeup_thread is None:
                self.wakeup_thread = WakeUpRobotThread(robot_controller=self.robot_controller)
                self.threads.append(self.wakeup_thread)

            self.wakeup_thread.rest()
        except Exception as e:
            self.logger.error("Error while setting the robot posture to rest: {}".format(e))

    # TOUCH
    # ------
    def enable_touch(self):
        self.robot_controller.touch()

    # BEHAVIORS
    # ---------
    def animate(self, animation_name=None):
        self.animation_thread.animate(animation_name=animation_name)

    def animated_say(self, message=None, animation_name=None):
        self.animation_thread.animated_say(message=message, animation_name=animation_name)

    # SPEECH
    # ------
    def say(self, message=None):
        to_say = "Hello!" if message is None else message
        if message is None:
            self.logger.info(to_say)
        self.animated_say(message=to_say)

    def start_playing(self, int_block, engagement_counter=0):
        if int_block is None:
            return False

        self.stop_playing = False
        self.previous_interaction_block = None
        self.current_interaction_block = int_block
        self.current_interaction_block.execution_mode = ExecutionMode.NEW
        self.logger.debug("Started playing the blocks")

        # set the engagement counter
        self.engagement_counter = int(engagement_counter)  # int(self.ui.engagementRepetitionsSpinBox.value())

        # ready to interact
        self.is_ready_to_interact = True

        # start engagement
        self.engagement(start=True)
        return True

    def get_next_interaction_block(self):
        if self.current_interaction_block is None:
            return None

        next_block = None
        connecting_edge = None
        self.logger.debug("Getting the next interaction block...")
        try:
            self.logger.debug("Execution Result: {}".format(self.animation_thread.execution_result))
            self.logger.info("Module Name: {} | Mode: {}\n\n".
                             format(self.current_interaction_block.interaction_module_name,
                                    self.current_interaction_block.execution_mode))
            if self.current_interaction_block.interaction_module_name and \
                    self.current_interaction_block.execution_mode is ExecutionMode.EXECUTING:
                self.execute_interaction_module()

            if self.current_interaction_block.is_hidden and self.interaction_module:
                connecting_edge = None
                next_block = self.interaction_module.get_next_interaction_block(self.current_interaction_block,
                                                                                self.animation_thread.execution_result)
            else:
                next_block, connecting_edge = self.current_interaction_block.get_next_interaction_block(
                    execution_result=self.animation_thread.execution_result)

            # complete execution
            self.current_interaction_block.execution_mode = ExecutionMode.COMPLETED

            # update previous block
            self.previous_interaction_block = self.current_interaction_block

        except Exception as e:
            self.logger.error("Error while getting the next block! {}".format(e))
        finally:
            return next_block, connecting_edge

    def interaction(self, start=False):
        self.logger.info("Interaction called with start = {}".format(start))

        if start is False:  # stop the interaction
            self.tablet_image(hide=True)
            self.is_ready_to_interact = False
            self.interaction_blocks = []  # empty the blocks
            self.engagement(start=False)

            self.robot_controller.is_interacting = False

            self.logger.info("Successfully stopped the interaction")

        elif self.is_ready_to_interact is True:  # start is True
            self.robot_controller.is_interacting = True
            self.customized_say()  # start interacting

    def stop_engagement_callback(self):
        # stop!
        self.engagement_counter = 0
        self.interaction(start=False)

    def engagement(self, start=False):
        """
        @param start = bool
        """
        self.logger.info("Engagement called with start = {} and counter = {}".format(start, self.engagement_counter))
        if start is True:
            self.engagement_thread.engagement(start=True)
            # self.face_detection_thread.face_detection(start=True)
        else:
            # decrease the engagement counter
            self.engagement_counter -= 1
            # stop the engagement if the counter is <= 0
            if self.engagement_counter <= 0:
                self.engagement_thread.engagement(start=False)
                # self.face_detection_thread.face_detection(start=False)

                self.has_finished_playing_observers.notify_all(True)

            else:  # continue
                self.is_ready_to_interact = True

    def verify_current_interaction_block(self):
        # if there are no more blocks, stop interacting
        if self.current_interaction_block is None or self.stop_playing is True:
            self.animation_thread.customized_say(reset=True)
            # stop interacting
            self.interaction(start=False)
            return False
        return True

    def customized_say(self, val=None):
        if self.verify_current_interaction_block() is False:
            return False

        # if self.animation_thread.isRunning():
        #     self.logger.debug("*** Animation Thread is still running!")
        #     return QTimer.singleShot(1000, self.customized_say)  # wait for the thread to finish

        self.block_controller.clear_selection()
        connecting_edge = None

        # check for remaining actions
        if self.execute_action_command() is True:
            return True

        if self.previous_interaction_block is None:  # interaction has just started
            self.previous_interaction_block = self.current_interaction_block
        else:
            # get the next block to say
            self.current_interaction_block, connecting_edge = self.get_next_interaction_block()

            # check if reached the end of the interaction_module
            if self.current_interaction_block is None and self.previous_interaction_block:
                if self.previous_interaction_block.is_hidden and self.interaction_module:
                    self.current_interaction_block = self.interaction_module.origin_block
                    self.current_interaction_block.execution_mode = ExecutionMode.COMPLETED
                    self.current_interaction_block, connecting_edge = self.get_next_interaction_block()

            if self.verify_current_interaction_block() is False:
                return False

        # execute the block
        self.current_interaction_block.execution_mode = ExecutionMode.EXECUTING

        if not self.current_interaction_block.is_hidden:
            self.current_interaction_block.set_selected(True)
            if connecting_edge is not None:
                connecting_edge.set_selected(True)

        self.current_interaction_block.volume = self.robot_volume

        # TODO:
        # self.face_detection_thread.face_detection()

        # get the result from the execution
        self.animation_thread.customized_say(interaction_block=self.current_interaction_block)

        return True

    def execute_interaction_module(self):
        self.interaction_module = ModuleFactory.create_module(self.current_interaction_block.interaction_module_name,
                                                              self.block_controller,
                                                              self.current_interaction_block)
        if self.interaction_module is None:
            return

        next_b = self.interaction_module.execute_module()

        if next_b is not None:
            next_b.is_hidden = True  # just in case!
            self.current_interaction_block.execution_mode = ExecutionMode.COMPLETED
            self.previous_interaction_block = self.current_interaction_block
            self.current_interaction_block = next_b

    def execute_action_command(self):
        # check for remaining actions
        if self.current_interaction_block.execution_mode is ExecutionMode.EXECUTING:
            if self.current_interaction_block.has_action(action_type=ActionCommand.PLAY_MUSIC):
                self.on_music_mode()
                return True
            elif self.current_interaction_block.has_action(action_type=ActionCommand.WAIT):
                self.on_wait_mode()
                return True
            elif self.current_interaction_block.has_action(action_type=ActionCommand.GET_RESERVATIONS):
                self.on_get_reservations()
                return True

        return False

    def on_get_reservations(self):
        get_reservations_command = self.current_interaction_block.action_command
        if get_reservations_command is not None:
            reservations = get_reservations_command.execute()

    def on_wait_mode(self):
        wait_time = 1  # 1s
        try:
            if self.current_interaction_block is not None:
                self.current_interaction_block.execution_mode = ExecutionMode.COMPLETED
                wait_command = self.current_interaction_block.action_command
                if wait_command is not None:
                    wait_time = wait_command.wait_time
        except Exception as e:
            self.logger.error("Error while setting wait time! {}".format(e))
        finally:
            self.logger.debug("Waiting for {} s".format(wait_time))
            QTimer.singleShot(wait_time * 1000, self.customized_say)

    def on_music_mode(self):
        if self.music_controller is None:
            self.logger.debug("Music player is not connected! Will skip playing music.")
            self.on_music_stop()
        else:
            self.current_interaction_block.action_command.music_controller = self.music_controller
            success = self.current_interaction_block.action_command.execute()
            if success is True:
                self.logger.debug("Playing now: {}".format(self.current_interaction_block.action_command.track))
                # TODO: specify wait time as track time when play_time is < 0
                # use action play time
                wait_time = self.current_interaction_block.action_command.play_time
                if wait_time <= 0:
                    wait_time = 30  # wait for 30s then continue
                anim_key = self.current_interaction_block.action_command.animations_key
                if anim_key is None or anim_key == "":
                    QTimer.singleShot(int(wait_time) * 1000, self.on_music_stop)
                else:
                    self.on_animation_mode(music_command=self.current_interaction_block.action_command,
                                           animation_time=int(wait_time))
                # QTimer.singleShot(wait_time * 1000, self.on_music_stop)
            else:
                self.logger.warning("Unable to play music! {}".format(self.music_controller.warning_message))
                self.on_music_stop()

    def on_animation_mode(self, music_command, animation_time=0):
        self.music_command = music_command
        self.animations_lst = config_helper.get_animations()[music_command.animations_key]
        self.animation_time = animation_time
        self.animation_counter = -1

        self.timer_helper.start()
        self.execute_next_animation()

    def on_animation_completed(self, val=None):
        if self.animation_thread.isRunning():
            self.logger.debug("*** Animation Thread is still running!")
            QTimer.singleShot(2000, self.on_animation_completed)  # wait for the thread to finish
        else:
            QTimer.singleShot(3000, self.execute_next_animation)

    def execute_next_animation(self):
        if self.music_command is None or len(self.animations_lst) == 0:
            QTimer.singleShot(1000, self.on_music_stop)
        elif self.timer_helper.elapsed_time() <= self.animation_time - 4:  # use 4s threshold
            # repeat the animations if the counter reached the end of the lst
            self.animation_counter += 1
            if self.animation_counter >= len(self.animations_lst):
                self.animation_counter = 0
            animation, message = self.get_next_animation(self.animation_counter)
            if message is None or message == "":
                self.animation_thread.animate(animation_name=animation)
            else:
                self.animation_thread.animated_say(message=message,
                                                   animation_name=animation)
        else:
            remaining_time = self.animation_time - self.timer_helper.elapsed_time()
            QTimer.singleShot(1000 if remaining_time < 0 else remaining_time * 1000, self.on_music_stop)

    def get_next_animation(self, anim_index):
        anim, msg = ("", "")
        try:
            animation_dict = self.animations_lst[anim_index]
            if len(animation_dict) > 0:
                anim = animation_dict.keys()[0]
                msg = animation_dict[anim]
        except Exception as e:
            self.logger.error("Error while getting next animation! {}".format(e))
        finally:
            return anim, msg

    def get_robot_voice(self):
        if self.current_interaction_block is None:
            return None

        return self.current_interaction_block.behavioral_parameters.voice

    def on_music_stop(self):
        self.logger.debug("Finished playing music.")
        try:
            if self.current_interaction_block is not None:
                self.current_interaction_block.execution_mode = ExecutionMode.COMPLETED
            if self.music_controller is not None:
                self.music_controller.pause()
        except Exception as e:
            self.logger.error("Error while stopping the music! {}".format(e))
        finally:
            self.customized_say()

    # TABLET
    # ------
    def tablet_image(self, hide=False):
        self.robot_controller.tablet_image(hide=hide)

    # MOVEMENT
    # --------
    def enable_moving(self):
        if self.animation_thread is None:
            return

        # self.animation_thread.moving_enabled = self.ui.enableMovingCheckBox.isChecked()
        self.logger.info("#### MOVING: {}".format(self.animation_thread.moving_enabled))
