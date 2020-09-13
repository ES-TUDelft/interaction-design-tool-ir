#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# SENSOR_ENUMS #
# ============ #
# List of enums related to robot cameras and sensors
#
# @author ES
# **

from __future__ import absolute_import
from es_common.enums.es_enum import ESEnum


class PixelResolution(ESEnum):
    R_160x120 = (0, [160, 120])
    R_320x240 = (1, [320, 240])
    R_640x480 = (2, [640, 480])
    R_1280x960 = (3, [1280, 960])

    def __init__(self, index, size):
        self.index = index
        self.size = size


class RobotCamera(ESEnum):
    TOP = 0
    BOTTOM = 1
    DEPTH = 2


class LedName(ESEnum):
    FACE = "FaceLeds"
    CHEST = "ChestLeds"


class Sonar(ESEnum):
    FRONT = "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
    BACK = "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"
