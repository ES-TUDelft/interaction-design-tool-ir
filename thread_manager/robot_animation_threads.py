#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================= #
# ROBOT_ANIMATION_THREADS #
# ======================= #
# Threads for animating the robot
#
# @author ES
# **

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal

from es_common.model.observable import Observable

"""
MOVE ROBOT THREAD
"""


class MoveRobotThread(QThread):
    movement_completed = pyqtSignal(bool)

    def __init__(self, robot_controller):
        QThread.__init__(self)
        self.robot_controller = robot_controller
        self.logger = logging.getLogger("MoveRobot Thread")
        self.x = 0
        self.y = 0,
        self.theta = 0

    def __del__(self):
        self.wait()

    def move_to(self, x=0, y=0, theta=0):
        self.x = x
        self.y = y
        self.theta = theta
        if not self.isRunning():
            self.run()

    def run(self):
        try:
            self.robot_controller.move_to(self.x, self.y, self.theta)
        except Exception as e:
            self.logger.error("Error while attempting to move the robot: {}".format(e))


"""
ROBOT ANIMATION THREAD
"""


class AnimateRobotThread(QThread):
    is_disconnected = pyqtSignal(bool)

    def __init__(self, robot_controller):
        QThread.__init__(self)

        self.logger = logging.getLogger("AnimateRobot Thread")

        self.animate_completed_observers = Observable()
        self.animated_say_completed_observers = Observable()
        self.customized_say_completed_observers = Observable()

        self.robot_controller = robot_controller
        self.robot_controller.observe_interaction_events(self.raise_completed_event, self.set_execution_result)

        self.animation_name = None
        self.message = None
        self.interaction_block = None
        self.behavioral_parameters = None
        self.is_first_block = True
        self.test_mode = False
        self.moving_enabled = False
        self.execution_result = None

    def __del__(self):
        self.wait()

    def animate(self, animation_name):
        self.robot_controller.execute_animation(animation_name=animation_name)
        self.logger.debug("Completed animation.")
        self.animate_completed_observers.notify_all(True)

    def animated_say(self, message=None, animation_name=None):
        self.robot_controller.animated_say(message=message,
                                           animation_name=animation_name)
        self.logger.debug("Completed animated say.")
        self.animated_say_completed_observers.notify_all(True)

    def customized_say(self, interaction_block=None, reset=False):
        if reset is True:
            self._reset()
            self.wait(10)
            self.logger.info("Recovered from waiting...")
        elif interaction_block is not None:
            self.interaction_block = interaction_block
            self.execution_result = None
            self.logger.info("Starting...")
            try:
                self.interaction_block.interaction_start_time = time.time()

                # change eye colors
                self.robot_controller.set_leds(led_color=self.interaction_block.behavioral_parameters.eye_color,
                                               duration=0.5)

                if self.test_mode is True:
                    self.robot_controller.customized_say(interaction_block=self.interaction_block)
                    self.customized_say(reset=True)
                else:
                    # load the web application if it's the first block
                    # TODO: use the "start" pattern as a trigger
                    if self.is_first_block is True:
                        # self.robot_controller.load_application(pconfig.app_name)
                        self.is_first_block = False
                    self.logger.info("Interaction block is: {}".format(self.interaction_block))
                    self.robot_controller.customized_say(interaction_block=self.interaction_block)

            except Exception as e:
                self.logger.error("Error in customized say: {}".format(e))

    def set_execution_result(self, val=None):
        self.logger.debug("User Answer: {}".format(val))

        self.execution_result = "{}".format(val) if val is not None else val
        self.raise_completed_event()

    def raise_completed_event(self, val=None):
        try:
            if self.test_mode is True:
                self.customized_say(reset=True)
            else:
                if self.interaction_block is not None:
                    self.interaction_block.interaction_end_time = time.time()
                self.logger.info("Block completed: notifying observers.")
                self.customized_say_completed_observers.notify_all(True)
        except Exception as e:
            self.logger.error("Error while raising completed event: {}".format(e))

    def _reset(self):
        self.robot_controller.posture(reset=True)
        self.move = False
        self.animation_name = None
        self.message = None
        self.interaction_block = None
        self.is_first_block = True
        self.test_mode = False

    def run(self):
        self.logger.info("Thread is up and running!")
