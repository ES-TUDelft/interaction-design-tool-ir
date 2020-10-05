#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# SPEECH_ACT #
# =========== #
# Model for the speech acts
#
# @author ES
# **

import logging

from es_common.enums.robot_enums import SpeechActsType


class SpeechAct(object):

    def __init__(self, message='', message_type=None):
        self.logger = logging.getLogger("SpeechAct")

        self.message = message
        self.message_type = SpeechActsType.INFORMAL if message_type is None else message_type

    def clone(self):
        return SpeechAct(self.message, self.message_type)

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        return {
            'message': self.message,
            'message_type': self.message_type.name
        }

    @staticmethod
    def create_speech_act(speech_dict):
        if speech_dict:
            return SpeechAct(speech_dict["message"], SpeechActsType[speech_dict["message_type"].upper()])

        return None
