#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ===================== #
# FACE_DETECTION_THREAD #
# ===================== #
# Threads for controlling the robot face detection stream
#
# @author ES
# **

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal


"""
ROBOT FACE DETECTION THREAD
"""


class RobotFaceDetectionThread(QThread):
    is_disconnected = pyqtSignal(bool)

    def __init__(self, robot_controller):
        QThread.__init__(self)

        self.logger = logging.getLogger("FaceDetectionThread")
        self.robot_controller = robot_controller
        self.stop_face_detection = False
        self.tracking_start_time = 0

    def __del__(self):
        self.wait()

    def face_detection(self, start=True):
        if start is False:
            self.stop_face_detection = True
        elif not self.isRunning():
            self.start()

    def run(self):
        self.stop_face_detection = False
        try:
            self.robot_controller.face_detection(start=True)
            self.tracking_start_time = time.time()

            while self.stop_face_detection is False:
                time.sleep(1)

            self.robot_controller.face_detection(start=False)
        except Exception as e:
            # self.is_disconnected.emit(True)
            self.logger.error("Error: {}".format(e))