#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================= #
# ROBOT_CONNECTION_THREAD #
# ======================= #
# Threads for animating the robot
#
# @author ES
# **

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal

from robot_manager.pepper.handler.connection_handler import ConnectionHandler

"""
ROBOT CONNECTION THREAD
"""


class RobotConnectionThread(QThread):
    is_connected = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)

        self.logger = logging.getLogger("ConnectionThread")

        self.robot_name = None
        self.robot_realm = None
        self.rie = None
        self.stay_connected = True

        self.connection_handler = None

    def __del__(self):
        self.wait()

    def stop_running(self):
        self.stay_connected = False

    def connect_to_robot(self, session_observer, robot_name=None, robot_realm=None):
        try:
            if self.connection_handler is None:
                self.connection_handler = ConnectionHandler()
            self.connection_handler.session_observers.add_observer(session_observer)
            self.robot_name = robot_name
            self.robot_realm = robot_realm

            if not self.isRunning():
                self.start()
        except Exception as e:
            self.logger.info("Error while staring the thread | {}".format(e))

    def run(self):
        try:
            self.logger.info("Connecting...")
            self.connection_handler.start_rie_session(robot_name=self.robot_name,
                                                      robot_realm=self.robot_realm)

            self.logger.info("Successfully connected to the robot")
            while self.stay_connected:
                time.sleep(1)

            self.logger.info("Disconnected from robot")
        except Exception as e:
            self.logger.error("Error while connecting to the robot! | {}".format(e))