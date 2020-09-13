#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ==================== #
# ROBOT_CAMERA_THREADS #
# ==================== #
# Threads for controlling the robot camera and the received image
#
# @author ES
# **

import cv2
import logging
import math
import time
from threading import Lock

import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal

import es_common.hre_config as pconfig
from es_common.controller.image_controller import ImageController
from robot_manager.pepper.enums.sensor_enums import PixelResolution
from es_common.utils.timer_helper import TimerHelper

"""
IMAGE THREAD
"""


class ImageControllerThread(QThread):
    changePixmap = pyqtSignal(QtGui.QImage)
    current_image_id = 0

    def __init__(self, mongo_dao, robot_controller, camera_id=pconfig.camera_id,
                 pixel_res=PixelResolution.R_640x480):
        QThread.__init__(self)
        self.logger = logging.getLogger("ImageControllerThread")
        self.camera_id = camera_id
        self.pixel_resolution = pixel_res
        self.draw_image = False
        self.show_fps = False

        self.robot_controller = robot_controller
        self.image_controller = None

        self.timer_helper = TimerHelper()
        self.mongo_dao = mongo_dao
        self.camera_thread = None
        self.current_image_lock = Lock()

    def __del__(self):
        self.wait()

    def update_image(self, draw_image=True, show_fps=True):
        self.draw_image = draw_image
        self.show_fps = show_fps
        if not self.isRunning():
            self.start()

    def run(self):
        self.image_controller = ImageController(output_dir=pconfig.output_dir,
                                                image_ext=pconfig.image_ext)

        self.camera_thread = CameraThread(robot_controller=self.robot_controller)
        self.camera_thread.setup_camera(camera_id=self.camera_id, resolution=int(self.pixel_resolution.index))
        self.camera_thread.image.connect(self.process_image)
        self.camera_thread.update_image()

    def process_image(self, image_id, image, img_fps, img_time):
        # TODO: if processing an image is needed
        if image is None: return
        processing_time = time.time()
        self.current_image_lock.acquire()
        if image_id < self.current_image_id:
            self.current_image_lock.release()
            self.logger.info("Image {} is dropped.".format(image_id))
            return
        else:  # update image id if it's newer than the current image, then release the lock
            self.current_image_id = image_id

        self.timer_helper.start()
        # Webcam: _, image = self.video_capture.read()

        # Draw image
        # emit signal to draw image on the UI
        if self.draw_image is True:
            self.emit_pixmap(frame=image,
                             img_fps=img_fps, img_time=img_time, processing_time=time.time() - processing_time)

        # release lock
        self.current_image_lock.release()

    def emit_pixmap(self, frame=None, img_fps=0, img_time=0, processing_time=0):
        if frame is None: return

        # put fps on the frame
        # fps = self._get_fps()
        if self.show_fps is True:  # and fps > 0:
            cv2.putText(frame,
                        "fps: {}, img_time: {:.3f}, process_time: {:.3f}".format(img_fps, img_time, processing_time),
                        (10, 30),  # top left
                        cv2.FONT_HERSHEY_SIMPLEX,  # font
                        0.4,  # scale
                        (245, 245, 0),
                        1  # cv2.LINE_AA # line type
                        )
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                         QtGui.QImage.Format_RGB888)
        res_size = self.pixel_resolution.size
        p = convertToQtFormat.scaled(res_size[0], res_size[1], QtCore.Qt.KeepAspectRatio)
        self.changePixmap.emit(p)

    def stop_camera(self):
        self.camera_thread.stop_image = True
        # Cleanup
        self.robot_controller.stop_camera()
        self.image_controller.cleanup()

    def get_output_dir(self):
        output_dir = ''
        return pconfig.output_dir if output_dir == '' else output_dir

    def _get_fps(self):
        self.timer_helper.stop()
        fps = 1 / (self.timer_helper.end_time - self.timer_helper.start_time)
        return math.ceil(fps)


"""
CAMERA THREAD
"""


class CameraThread(QThread):
    image = pyqtSignal(float, np.ndarray, float, float)

    def __init__(self, robot_controller):
        QThread.__init__(self)

        self.logger = logging.getLogger("CameraThread")
        self.robot_controller = robot_controller
        self.stop_image = False
        self.timer_helper = TimerHelper()

    def __del__(self):
        self.wait()

    def setup_camera(self, camera_id, resolution):
        self.robot_controller.setup_camera(camera_id=camera_id, resolution=resolution)

    def update_image(self):
        if not self.isRunning():
            self.start()

    def _get_fps(self):
        self.timer_helper.stop()
        fps = 1 / (self.timer_helper.end_time - self.timer_helper.start_time)
        return math.ceil(fps)

    def run(self):
        while self.stop_image is False:
            self.timer_helper.start()
            i_t = time.time()
            img = self.robot_controller.get_image()
            if img is None:
                self.logger.error("Error: image received is 'None'")
            else:
                self.image.emit(time.time(), img, self._get_fps(), time.time() - i_t)
