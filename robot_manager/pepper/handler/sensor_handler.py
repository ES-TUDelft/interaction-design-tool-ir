#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============== #
# SENSOR_HANDLER #
# ============== #
# Handler class for controlling the robot's sensors
#
# @author ES
# **

import logging

from es_common.enums.led_enums import LedColor
from robot_manager.pepper.enums.sensor_enums import Sonar, LedName


class SensorHandler(object):

    def __init__(self, session=None):
        self.logger = logging.getLogger("SensorHandler")
        self.session = session

    def get_distance(self, sonar=Sonar.FRONT):
        self.logger.info("Distance is not implemented!")
        return 0

    def set_leds(self, led_name=LedName.FACE, led_color=LedColor.WHITE, duration=0.5):
        self.logger.info("SetLeds is not implemented!")
        # self.leds.fadeRGB(led_name.value, led_color.r, led_color.g, led_color.b, duration)

    def led_animation(self, duration=2.0):
        self.logger.info("LedAnimation is not implemented!")
        # self.leds.rasta(duration)
