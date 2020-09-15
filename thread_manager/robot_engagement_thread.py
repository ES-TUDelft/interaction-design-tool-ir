#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================= #
# ROBOT_ENGAGEMENT_THREAD #
# ======================= #
# Threads for controlling the robot engagement and dialog
#
# @author ES
# **

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal

"""
ROBOT ENGAGEMENT THREAD
"""


class RobotEngagementThread(QThread):
    is_engaged = pyqtSignal(bool)
    is_disconnected = pyqtSignal(bool)

    def __init__(self, robot_controller):
        QThread.__init__(self)

        self.logger = logging.getLogger("EngagementThread")
        self.robot_controller = robot_controller
        self.stop_engagement = False

    def __del__(self):
        self.wait()

    def engagement(self, start=True):
        if start is False:
            self.stop_running()
        elif not self.isRunning():
            self.start()

    def stop_running(self):
        self.stop_engagement = True

    def run(self):
        self.stop_engagement = False
        try:
            self.robot_controller.engagement(start=True)
            while not self.stop_engagement:
                time.sleep(1)

            if self.robot_controller:
                self.robot_controller.engagement(start=False)
                # self.robot_controller.posture(reset=True)
        except Exception as e:
            self.is_disconnected.emit(True)
            self.logger.error("Error while connecting to the robot: {}".format(e))
