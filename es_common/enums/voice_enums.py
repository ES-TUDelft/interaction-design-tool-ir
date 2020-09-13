#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# SPEECH_ENUMS #
# ============ #
# List of enums for managing robot speech
#
# @author ES
# **

from es_common.enums.es_enum import ESEnum


class VoiceTag(ESEnum):
    SPEED = "rspd"
    PITCH = "vct"
    PROSODY = "bound"
    STYLE = "style"
    VOLUME = "vol"
    PAUSE = "pau"
    RESET = "rst"


class VoiceName(ESEnum):
    CLAIRE = "claire"
    NAO_ENU = "naoenu"
    NAO_MNC = "naomnc"


class VoiceStyle(ESEnum):
    NEUTRAL = "normal"
    JOYFUL = "playful"
    DIDACTIC = "narrative"


class VoiceProsody(ESEnum):
    WEAK = 0  # W = No silence in speech
    STRONG = 1  # S = Silence in speech
    # NOBOUND = -1      # N = No Bound
