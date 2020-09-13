#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =================== #
# WAKEUP_ROBOT_THREAD #
# =================== #
# Threads for animating the robot
#
# @author ES
# **

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal

"""
WAKE UP ROBOT THREAD
"""


class WakeUpRobotThread(QThread):
    awake_signal = pyqtSignal(bool)

    def __init__(self, robot_controller):
        QThread.__init__(self)
        self.robot_controller = robot_controller
        self.wakeup = False

    def __del__(self):
        self.wait()

    def stand(self):
        self.wakeup = True
        if not self.isRunning():
            self.start()

    def rest(self):
        self.wakeup = False
        if not self.isRunning():
            self.start()

    def run(self):
        self.robot_controller.posture(wakeup=self.wakeup)
        self.awake_signal.emit(True)
