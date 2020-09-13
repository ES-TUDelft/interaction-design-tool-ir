#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# ROBOT_VOICE #
# =========== #
# Model for controlling the robot's voice effects
#
# @author ES
# **

import logging
import random

import es_common.hre_config as pconfig
from es_common.enums.voice_enums import VoiceName, VoiceProsody, VoiceStyle


class RobotVoice(object):

    def __init__(self, randomize=True):
        self.logger = logging.getLogger("RobotVoice")

        # init parameters
        self.__name = VoiceName.NAO_ENU
        self.__speed = pconfig.default_voice_speed  # (random.randrange(70, 140, 10)) if randomize is True else
        self.__pitch = pconfig.default_voice_pitch  # (float(random.randrange(7, 14, 1)) / 10.0) if randomize is True
        self.__prosody = VoiceProsody.WEAK
        self.__style = VoiceStyle.NEUTRAL
        self.__volume = pconfig.default_voice_volume

    def clone(self):
        rv = RobotVoice()
        rv.name = VoiceName[self.name.name]
        rv.speed = self.speed
        rv.pitch = self.pitch
        rv.prosody = VoiceProsody[self.prosody.name]
        # rv.style = VoiceStyle[self.style.name] # uncomment if needed!
        rv.volume = self.volume

        return rv

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        return {
            'name': self.name.name,
            'speed': self.speed,
            'pitch': self.pitch,
            'prosody': self.prosody.name,
            # 'style': self.style.name,
            'volume': self.volume,
        }

    @staticmethod
    def create_robot_voice(rv_dict):
        rv = RobotVoice()
        if rv_dict:
            rv.name = VoiceName[rv_dict["name"]]
            rv.speed = float(rv_dict["speed"])
            rv.pitch = float(rv_dict["pitch"])
            rv.prosody = VoiceProsody[rv_dict["prosody"]]
            # rv.style = VoiceStyle[rv_dict["style"]]
            rv.volume = float(rv_dict["volume"])

        return rv

    # ===========
    # PROPERTIES
    # ===========
    """
    NAME
    """

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value=VoiceName.CLAIRE):
        self.__name = value

    """
    SPEED
    """

    @property
    def speed(self):
        return self.__speed

    @speed.setter
    def speed(self, value):
        self.__speed = value if self._check_value(value,
                                                  pconfig.voice_speed_range[0],
                                                  pconfig.voice_speed_range[1],
                                                  "speed") is True else pconfig.default_voice_speed

    """
    PITCH
    """

    @property
    def pitch(self):
        return self.__pitch

    @pitch.setter
    def pitch(self, value):
        self.__pitch = value if self._check_value(value,
                                                  pconfig.voice_pitch_range[0],
                                                  pconfig.voice_pitch_range[1],
                                                  "pitch") is True else pconfig.default_voice_pitch

    """
    PROSODY
    """

    @property
    def prosody(self):
        return self.__prosody

    @prosody.setter
    def prosody(self, value=VoiceProsody.WEAK):
        self.__prosody = value

    """
    STYLE
    """

    @property
    def style(self):
        return self.__style

    @style.setter
    def style(self, value=VoiceStyle.NEUTRAL):
        self.__style = value

    """
    VOLUME
    """

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value=pconfig.default_voice_volume):
        if self._check_value(value, pconfig.voice_volume_range[0], pconfig.voice_volume_range[1], "volume") is True:
            self.__volume = value

    def _check_value(self, value, start, stop, name):
        if start <= value <= (stop + 1):
            return True
        else:
            self.logger.error("*** Please provide a {} value in range: [{}, {}]".format(name, start, stop))
            return False
