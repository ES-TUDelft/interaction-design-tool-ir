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


class GazePattern(ESEnum):
    FIXATED = 0
    DIVERTED = 1


class GesturesType(ESEnum):
    CLOSE = 0
    OPEN = 1


class SpeechActsType(ESEnum):
    FORMAL = 0
    INFORMAL = 1


class InteractionPattern(ESEnum):
    MONOLOGUE = 0
    QUESTION = 1
