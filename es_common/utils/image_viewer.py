#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# IMAGE_VIEWER #
# ============ #
# Helper class for drawing and saving images
#
# @author ES
# **

import logging
import cv2
import os

import es_common.hre_config as pconfig


class ImageViewer:
    def __init__(self, output_dir=pconfig.output_dir,
                 image_name=pconfig.image_name, image_ext=pconfig.image_ext,
                 video_name=pconfig.video_name, video_ext=pconfig.video_ext, video_fps=pconfig.video_fps):
        self.logger = logging.getLogger("ImageViewer")

        self.video_writer = None
        self.output_dir = output_dir
        self.image_name = image_name
        self.image_ext = image_ext
        self.video_name = video_name
        self.video_ext = video_ext
        self.video_fps = video_fps
        self.logger.info("Processed images will be stored in: " + self.output_dir)

    def release(self):
        return False if self.video_writer is None else self.video_writer.release()

    def reset_video_writer(self):
        self.video_writer = None

    def update(self, image, draw_image=True, save_video=False, fps=0):
        if image is None:
            return False

        # put text
        if fps > 0:
            cv2.putText(image,
                        "fps: " + str(fps),
                        (10, 30),  # top left
                        cv2.FONT_HERSHEY_SIMPLEX,  # font
                        0.5,  # scale
                        (245, 245, 0),
                        2  # cv2.LINE_AA # line type
                        )

        if draw_image is True:
            self.draw(image)

        if save_video is True:
            self.write_to_video(image)

    def write_to_video(self, image):
        """
        Write to video
        """
        if self.video_writer is None:
            # init video writer
            h, w, _ = image.shape
            v_path = os.path.join(self.output_dir, '{}'.format(self.video_name + "." + self.video_ext))
            self.logger.info("*** VIDEO: " + v_path)
            self.video_writer = cv2.VideoWriter(v_path,
                                                cv2.VideoWriter_fourcc(*'MJPG'),
                                                self.video_fps,
                                                (int(w), int(h)), True
                                                )

        self.video_writer.write(image)

    def draw(self, image):
        """
        Draws raw image
        """
        cv2.imshow('Pepper Camera Feed', image)
        cv2.waitKey(1)
