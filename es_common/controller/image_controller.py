#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================ #
# IMAGE_CONTROLLER #
# ================ #
# Controller class for updating the image received from the robot's camera.
#
# @author ES
# **

import logging
import time

from es_common.utils.image_viewer import ImageViewer


class ImageController(object):
    def __init__(self, output_dir="", image_ext="jpg"):
        self.logger = logging.getLogger("Image Controller")

        # Image properties
        self.output_dir = output_dir
        self.image_ext = image_ext
        self.image_name = None
        self.image_viewer = ImageViewer(output_dir=output_dir, image_name=self.get_image_name(),
                                        image_ext=image_ext, video_name=self.get_image_name())

    def update_image(self, image, draw=True, fps=0):
        self.image_viewer.update(image=image,
                                 draw_image=draw,
                                 fps=fps
                                 )

    # -------------- #
    # Helper Methods #
    # -------------- #
    def get_image_name(self):
        if self.image_name is None:
            self.image_name = "image_" + str(time.time())
        return self.image_name

    def cleanup(self):
        self.image_viewer.release()
