#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# INTERACTION_CONTROLLER #
# =========================== #
# Class for managing the interaction flow with the robot.
#
# @author ES
# **

import logging
import time

from block_manager.enums.block_enums import ExecutionMode
from data_manager.controller.db_stream_controller import DBStreamController
from es_common.enums.command_enums import ActionCommand
from es_common.factory.module_factory import ModuleFactory
from es_common.model.observable import Observable
from es_common.utils.qt import QTimer
from es_common.utils.timer_helper import TimerHelper
from interaction_manager.utils import config_helper


class InteractionController(object):
    def __init__(self, block_controller, music_controller=None):
        self.logger = logging.getLogger("Interaction Controller")

        self.block_controller = block_controller
        self.music_controller = music_controller
        self.db_stream_controller = DBStreamController()
        self.timer_helper = TimerHelper()
        self.music_command = None
        self.animations_lst = []
        self.animation_time = 0
        self.animation_counter = -1
        self.robot_volume = 50

        self.robot_name = None
        self.robot_realm = None

        self.current_interaction_block = None
        self.previous_interaction_block = None
        self.interaction_module = None
        self.is_interacting = False

        self.execution_result = None
        self.tablet_input = None
        self.has_finished_playing_observers = Observable()
        self.threads = []
        self.on_connected_observers = Observable()

        self.start_listening_to_db_stream()

    def connect_to_robot(self, robot_name=None, robot_realm=None, robot_ip=None, robot_port=None):
        self.robot_name = robot_name
        self.robot_realm = robot_realm

        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="connectRobot",
                                             data_dict={"connectRobot": {"robotName": self.robot_name,
                                                                         "robotRealm": self.robot_realm,
                                                                         "robotIP": robot_ip,
                                                                         "robotPort": robot_port},
                                                        "timestamp": time.time()})

    def on_connect(self, data_dict=None):
        try:
            self.logger.info("Connect data received: {}".format(data_dict))
            if data_dict and data_dict["isConnected"] is True:
                self.logger.debug("Connected...")
                self.on_connected_observers.notify_all(True)
            else:
                self.logger.info("Robot is not connected!")
        except Exception as e:
            self.logger.error("Error while extracting isConnected: {} | {}".format(data_dict, e))
            self.execution_result = None

    def disconnect(self):
        try:
            self.logger.info("Disconnecting...")

            self.engagement(start=False)
            self.db_stream_controller.stop_db_stream()

            self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                                 data_key="disconnectRobot",
                                                 data_dict={"disconnectRobot": True, "timestamp": time.time()})
            self.logger.info("Disconnection was successful.")
        except Exception as e:
            self.logger.error("Error while disconnecting: {}".format(e))

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
        success = False
        conn = None
        try:
            conn = self.db_stream_controller.find_one(self.db_stream_controller.robot_collection, "isConnected")
            if conn and conn["isConnected"] is True:
                success = True
        except Exception as e:
            self.logger.error("Error while extracting isConnected: {} | {}".format(conn, e))
        finally:
            return success

    def start_listening_to_db_stream(self):
        observers_dict = {
            "isConnected": self.on_connect,
            "isExecuted": self.on_block_executed,
            "isDisengaged": self.on_disengaged,
            "startInteraction": self.on_start_interaction,
            "tabletInput": self.on_tablet_input
        }
        self.db_stream_controller.start_db_stream(observers_dict=observers_dict,
                                                  db_collection=self.db_stream_controller.robot_collection,
                                                  target_thread="qt")

    def on_block_executed(self, data_dict=None):
        try:
            if self.is_interacting is False:
                self.logger.info("Not in interaction mode!")
                return False

            self.logger.info("isExecuted data received: {}".format(data_dict))
            self.execution_result = data_dict["isExecuted"]["executionResult"]
            self.execute_next_block()
        except Exception as e:
            self.logger.error("Error while extracting isExecuted block: {} | {}".format(data_dict, e))
            self.execution_result = None

    def on_tablet_input(self, data_dict=None):
        try:
            if self.is_interacting is False:
                self.logger.info("Not in interaction mode!")
                return False

            self.logger.info("Tablet data received: {}".format(data_dict))
            self.tablet_input = data_dict["tabletInput"]
            self.execution_result = data_dict["tabletInput"]
            self.execute_next_block()
        except Exception as e:
            self.logger.error("Error while extracting tablet data: {} | {}".format(data_dict, e))
            self.tablet_input = None
            self.execution_result = None

    def on_disengaged(self, data_dict=None):
        try:
            self.logger.info("Disengaged data received: {}".format(data_dict))
            self.execution_result = ""
            self.stop_playing()
        except Exception as e:
            self.logger.error("Error while extracting disengaged data: {} | {}".format(data_dict, e))

    def update_speech_certainty(self, speech_certainty=40.0):
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="speechCertainty",
                                             data_dict={"speechCertainty": speech_certainty, "timestamp": time.time()})

    def update_db_data(self, data_key, data_value):
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key=data_key,
                                             data_dict={data_key: data_value, "timestamp": time.time()})

    def wakeup_robot(self):
        success = False
        try:
            self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                                 data_key="wakeUpRobot",
                                                 data_dict={"wakeUpRobot": True, "timestamp": time.time()})
            success = True
        except Exception as e:
            self.logger.error("Error while waking up the robot! | {}".format(e))
        finally:
            return success

    def rest_robot(self):
        try:
            self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                                 data_key="restRobot",
                                                 data_dict={"restRobot": True, "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while setting the robot posture to rest: {}".format(e))

    # TOUCH
    # ------
    def enable_touch(self):
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="enableTouch",
                                             data_dict={"enableTouch": True, "timestamp": time.time()})

    # BEHAVIORS
    # ---------
    def animate(self, animation_name=None):
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="animateRobot",
                                             data_dict={"animateRobot": {"animation": animation_name, "message": ""},
                                                        "timestamp": time.time()})

    def animated_say(self, message=None, animation_name=None):
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="animateRobot",
                                             data_dict={
                                                 "animateRobot": {"animation": animation_name, "message": message},
                                                 "timestamp": time.time()})

    def customized_say(self, interaction_block):
        if interaction_block is None:
            return

        block_to_execute = interaction_block.clone()
        if "{answer}" in block_to_execute.message and block_to_execute.execution_result:
            block_to_execute.message = block_to_execute.message.format(answer=block_to_execute.execution_result.lower())

        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="interactionBlock",
                                             data_dict={"interactionBlock": block_to_execute.to_dict,
                                                        "timestamp": time.time()})

    # SPEECH
    # ------
    def say(self, message=None):
        to_say = "Hello!" if message is None else message
        if message is None:
            self.logger.info(to_say)
        self.animated_say(message=to_say)

    def on_start_interaction(self, data_dict=None):
        if self.is_interacting:
            self.logger.info("Interaction is in progress...")
            return False

        self.logger.info("Starting the interaction!")
        self.start_playing(int_block=self.get_starting_block())

    def start_playing(self, int_block):
        if int_block is None:
            self.is_interacting = False
            self.logger.warning("Couldn't start the interaction!")
            return False

        self.is_interacting = True

        self.previous_interaction_block = None
        self.current_interaction_block = int_block
        self.current_interaction_block.execution_mode = ExecutionMode.NEW
        self.logger.debug("Started playing the blocks")

        self.execute_next_block()  # start interacting

    def stop_playing(self):
        # self.tablet_image(hide=True)
        self.is_interacting = False
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="resumeEngagement",
                                             data_dict={"resumeEngagement": True, "timestamp": time.time()})

        self.has_finished_playing_observers.notify_all(True)
        self.logger.info("Stopped interacting.")

    def get_starting_block(self):
        try:
            # check if the scene contains a valid start block
            block = self.block_controller.get_block(pattern="start")
            if block is None:
                self.logger.warning("The scene doesn't contain a starting block! "
                                    "Please add a 'START' block to play the interaction!")
                return None

            self.logger.info("Found a starting block.")
            return block.parent
        except Exception as e:
            self.logger.error("Error while getting the start block: {}".format(e))
            return None

    def execute_next_block(self):
        try:
            self.logger.info("Executing next block.\n")
            self.block_controller.clear_selection()
            connecting_edge = None

            # check for remaining actions; otherwise, continue
            if self.current_interaction_block.action_command and \
                    self.current_interaction_block.execution_mode is ExecutionMode.EXECUTING:
                self.execute_action_command()
            else:
                # check if the interaction has just started
                if self.previous_interaction_block is None:
                    self.previous_interaction_block = self.current_interaction_block
                else:
                    # get the next block to say
                    self.current_interaction_block, connecting_edge = self.get_next_interaction_block()

                if self.verify_current_interaction_block() is False:
                    return False

                # change the block status
                self.current_interaction_block.execution_mode = ExecutionMode.EXECUTING
                # update selection
                self.current_interaction_block.set_selected(True)
                if connecting_edge is not None:
                    connecting_edge.set_selected(True)
                self.block_controller.update()

                # send a request to say the robot message
                self.customized_say(interaction_block=self.current_interaction_block)
        except Exception as e:
            self.logger.error("Error while executing next block: {}".format(e))

    def get_next_interaction_block(self):
        if self.current_interaction_block is None:
            return None

        next_block = None
        connecting_edge = None

        self.logger.info("Getting the next interaction block...")
        try:
            # 1- Check for the design module and execute it
            if self.current_interaction_block.design_module and \
                    self.current_interaction_block.execution_mode is ExecutionMode.EXECUTING:
                self.execute_interaction_module()

            # 2- When the interaction module exists, get the next block from it
            if self.current_interaction_block.is_hidden and self.interaction_module:
                connecting_edge = None
                next_block = self.interaction_module.get_next_interaction_block(self.current_interaction_block,
                                                                                self.execution_result)
                # check if reached the end of the interaction_module
                if next_block is None and self.previous_interaction_block:
                    self.current_interaction_block = self.interaction_module.origin_block

            # 3- Otherwise, Get the next block from the current design
            if next_block is None:
                next_block, connecting_edge = self.current_interaction_block.get_next_interaction_block(
                    execution_result=self.execution_result)

            # Change current block status
            self.current_interaction_block.execution_mode = ExecutionMode.COMPLETED
            # update previous block
            self.previous_interaction_block = self.current_interaction_block

            return next_block, connecting_edge
        except Exception as e:
            self.logger.error("Error while getting the next block! {}".format(e))
            return next_block, connecting_edge

    def engagement(self, start=False):
        """
        @param start = bool
        """
        self.logger.info("Engagement called with start = {}".format(start))
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="startEngagement",
                                             data_dict={"startEngagement": start, "timestamp": time.time()})

    def verify_current_interaction_block(self):
        # if there are no more blocks, stop interacting
        if self.current_interaction_block is None:
            # stop interacting
            self.stop_playing()
            return False
        return True

    def execute_interaction_module(self):
        self.interaction_module = ModuleFactory.create_module(self.current_interaction_block.design_module,
                                                              self.current_interaction_block,
                                                              self.block_controller)
        self.logger.info("Interaction module: {}".format(self.interaction_module))
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
            QTimer.singleShot(wait_time * 1000, self.execute_next_block)

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
                self.animate(animation_name=animation)
            else:
                self.animated_say(message=message,
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
            self.execute_next_block()

    # TABLET
    # ------
    def tablet_image(self, hide=False):
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="hideTabletImage",
                                             data_dict={"hideTabletImage": True, "timestamp": time.time()})

    # PROPERTIES
    # ==========

    @property
    def is_interacting(self):
        return self._is_interacting

    @is_interacting.setter
    def is_interacting(self, val=False):
        self._is_interacting = val
        self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                             data_key="isInteracting",
                                             data_dict={"isInteracting": val, "timestamp": time.time()})
