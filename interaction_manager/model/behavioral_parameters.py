#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ===================== #
# BEHAVIORAL_PARAMETERS #
# ===================== #
# Model for controlling the robot's behavioral parameters
#
# @author ES
# **

import logging
import random

import es_common.hre_config as pconfig
from es_common.enums.led_enums import LedColor
from es_common.model.robot_voice import RobotVoice
from es_common.enums.speech_enums import GesturesType, GazePattern, SpeechActsType
from interaction_manager.model.speech_act import SpeechAct
from interaction_manager.model.gesture import Gesture


class BehavioralParameters(object):
    def __init__(self, randomize=True):
        self.logger = logging.getLogger("BehavioralParameters")

        self.voice = RobotVoice()
        self.speech_act = SpeechAct()
        self.gaze_pattern = GazePattern.FIXATED

        self.gesture = Gesture()

        # proxemics_range = [int(i * 100) for i in pconfig.proxemics_range]
        self.proxemics = pconfig.default_proxemics
        # (float(random.randrange(proxemics_range[0], proxemics_range[1], 25)) / 100.0)
        #           if randomize is True else pconfig.default_proxemics

        self.eye_color = LedColor.GREEN
        # list(LedColor)[random.randint(0, len(LedColor.keys()) - 1)] if randomize is True else LedColor.WHITE

    @property
    def to_dict(self):
        beh_dict = {
            'voice': self.voice.to_dict,  # dict
            'gaze_pattern': self.gaze_pattern.name,
            'proxemics': self.proxemics,
            'eye_color': self.eye_color.name
        }
        # add speech act and gesture properties
        beh_dict.update(self.speech_act.to_dict)
        beh_dict.update(self.gesture.to_dict)

        return beh_dict

    def clone(self, beh_param=None):
        bp = BehavioralParameters() if beh_param is None else beh_param.clone()
        bp.voice = self.voice.clone()
        bp.speech_act = self.speech_act.clone()
        bp.gesture = self.gesture.clone()
        bp.gaze_pattern = GazePattern[self.gaze_pattern.name]
        bp.proxemics = self.proxemics
        bp.eye_color = LedColor[self.eye_color.name]

        return bp

    # ============== #
    # HELPER METHODS #
    # ============== #
    @staticmethod
    def create_behavioral_parameters(beh_dict):
        bp = BehavioralParameters()
        if beh_dict:
            bp.voice = RobotVoice.create_robot_voice(rv_dict=beh_dict['voice'])
            bp.speech_act = SpeechAct(beh_dict['message'], SpeechActsType[beh_dict['message_type'].upper()])
            bp.gaze_pattern = GazePattern[beh_dict['gaze_pattern'].upper()]
            bp.gesture = Gesture(beh_dict["gestures"], GesturesType[beh_dict["gestures_type"].upper()])
            bp.proxemics = float(beh_dict['proxemics'])
            bp.eye_color = LedColor[beh_dict['eye_color'].upper()]

        return bp

    def set_parameters(self, p_name, behavioral_parameters):
        if "gestures_type" in p_name.lower():
            self.gesture.gestures_type = behavioral_parameters.gesture.gestures_type
        elif "gaze" in p_name.lower():
            self.gaze_pattern = behavioral_parameters.gaze_pattern
        elif "proxemic" in p_name.lower():
            self.proxemics = behavioral_parameters.proxemics
        elif "voice" in p_name.lower():
            self.voice = behavioral_parameters.voice.clone()
        elif "eye" in p_name.lower():
            self.eye_color = behavioral_parameters.eye_color
        else:  # set everything except speech acts!
            self.gestures_type = behavioral_parameters.gestures_type
            self.gaze_pattern = behavioral_parameters.gaze_pattern
            self.proxemics = behavioral_parameters.proxemics
            self.voice = behavioral_parameters.voice.clone()
            self.eye_color = behavioral_parameters.eye_color

    @property
    def speech_act(self):
        return self.__speech_act

    @speech_act.setter
    def speech_act(self, speech_act):
        self.__speech_act = speech_act.clone()

    @property
    def gesture(self):
        return self.__gesture

    @gesture.setter
    def gesture(self, gesture):
        self.__gesture = gesture.clone()

    @property
    def gestures_type(self):
        return self.gesture.gestures_type

    @gestures_type.setter
    def gestures_type(self, gestures_type):
        self.gesture.gestures_type = gestures_type

    @property
    def proxemics(self):
        return self.__proxemics

    @proxemics.setter
    def proxemics(self, value):
        self.__proxemics = value if self._check_value(value,
                                                      pconfig.proxemics_range[0],
                                                      pconfig.proxemics_range[1]) is True else pconfig.default_proxemics

    def _check_value(self, value, start, stop):
        if start <= value <= (stop + 1):
            return True
        else:
            self.logger.error("*** Please provide a value in range: [{}, {}]".format(start, stop))
            return False
