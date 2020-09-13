#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# ROBOT_CAMERA #
# ============ #
# Model for controlling the properties of the robot's camera
#
# @author ES
# **

import logging


class RobotCamera(object):
    def __init__(self, camera_id, resolution, image_ext, output_dir):
        self.logger = logging.getLogger("Robot Camera")
        self.camera_id = camera_id
        self.resolution = resolution
        self.image_ext = image_ext
        self.output_dir = output_dir
