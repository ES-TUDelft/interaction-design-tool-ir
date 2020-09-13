#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# GESTURE #
# =========== #
# Model for the robot gesture
#
# @author ES
# **

import logging

import es_common.hre_config as pconfig
from es_common.enums.speech_enums import GesturesType


class Gesture(object):

    def __init__(self, gestures=None, gestures_type=None):
        self.logger = logging.getLogger("Gesture")

        self.gestures = {"open": "", "close": ""} if gestures is None else gestures
        self.gestures_type = GesturesType.OPEN if gestures_type is None else gestures_type

    def clone(self):
        return Gesture(self.gestures, self.gestures_type)

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        return {
            'gestures': self.gestures,
            'gestures_type': self.gestures_type.name
        }

    def set_gestures(self, open_gesture="", close_gesture=""):
        self.gestures = {
            "open": open_gesture,
            "close": close_gesture
        }

    @staticmethod
    def create_gesture(gesture_dict):
        if gesture_dict:
            return Gesture(gesture_dict["gestures"], GesturesType[gesture_dict["gestures_type"].upper()])

        return None
