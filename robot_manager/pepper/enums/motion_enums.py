#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# MOTION_ENUMS #
# ============ #
# List of enums related to robot motion and animation
#
# @author ES
# **

from es_common.enums.es_enum import ESEnum


class Animation(ESEnum):
    AGREE = 'animations/Stand/Gestures/Yes_3'
    CHEER = 'animations/Stand/Gestures/Hey_2'
    DISAGREE = 'animations/Stand/Gestures/No_1'
    MAD = 'animations/Stand/Gestures/YouKnowWhat_1'
    GOODBYE = 'animations/Stand/Gestures/Hey_3'
    HIGH_FIVE = 'animations/Stand/Gestures/ShowSky_9'
    ME = 'animations/Stand/Gestures/Me_1'
    NOD = 'animations/Stand/Gestures/Hey_8'
    OPEN_HANDS = 'animations/Stand/Gestures/Please_1'
    POINT_AT = 'animations/Stand/Gestures/You_1'
    SHOW_SKY = 'animations/Stand/Gestures/ShowSky_1'
    SHOW_TABLET = 'animations/Stand/Gestures/ShowTablet_2'
    EMBARRASSED = 'animations/Stand/Emotions/Neutral/Embarrassed_1'
    TELL_ME_MORE = 'animations/Stand/Gestures/Hey_9'
    CLOSED_HANDS = 'animations/Stand/Gestures/Thinking_1'
    WAVE = 'animations/Stand/Gestures/Hey_1'


class PersonRelatedGestures(ESEnum):
    OPEN_HANDS = 'animations/Stand/Gestures/Please_1'  # courtesy
    WAVE = 'animations/Stand/Gestures/Hey_1'  # courtesy / attentiveness
    GOODBYE = 'animations/Stand/Gestures/Hey_3'  # courtesy
    NOD = 'animations/Stand/Gestures/Hey_8'  # attentiveness
    AGREE = 'animations/Stand/Gestures/Yes_3'  # attentiveness
    TELL_ME_MORE = 'animations/Stand/Gestures/Hey_9'  # attentiveness
    POINT_AT = 'animations/Stand/Gestures/You_1'  # professionalism
    SHOW_TABLET = 'animations/Stand/Gestures/ShowTablet_2'  # professionalism
    CALM_DOWN = 'animations/Stand/Gestures/CalmDown_1'  # Empathy
    # CALM_DOWN_6 = 'animations/Stand/Gestures/CalmDown_6'
    CLOSED_HANDS = 'animations/Stand/Gestures/Thinking_1'
    HIGH_FIVE = 'animations/Stand/Gestures/ShowSky_9'  # Enthusiasm
    CHEER = 'animations/Stand/Gestures/Hey_2'  # Enthusiasm
    HYSTERICAL = 'animations/Stand/Emotions/Positive/Hysterical_1'  # Enthusiasm
    ENTHUSIASTIC_4 = 'animations/Stand/Gestures/Enthusiastic_4'  # Enthusiasm
    ENTHUSIASTIC_5 = 'animations/Stand/Gestures/Enthusiastic_5'  # Enthusiasm
    EMBARRASSED = 'animations/Stand/Emotions/Neutral/Embarrassed_1'  # Embarrassed
    ME = 'animations/Stand/Gestures/Me_1'
    DISAGREE = 'animations/Stand/Gestures/No_1'  # Disagreement
    MAD = 'animations/Stand/Gestures/YouKnowWhat_1'
    BORED = 'animations/Stand/Emotions/Negative/Bored_1'
    HAPPY = 'animations/Stand/Emotions/Positive/Happy_4'
    DESPERATE = 'animations/Stand/Gestures/Desperate_1'


class TaskRelatedGestures(ESEnum):
    POINT_AT = 'animations/Stand/Gestures/You_1'  # knowledgeable
    SHOW_TABLET = 'animations/Stand/Gestures/ShowTablet_2'  # prepared / knowledgeable
    EXPLAIN = 'animations/Stand/Gestures/Please_1'  # thorough
    SHOW_SKY = 'animations/Stand/Gestures/ShowSky_1'  # thorough
    BUT = 'animations/Stand/Gestures/But_1'  # knowledgeable
    CHOICE = 'animations/Stand/Gestures/Choice_1'  # thorough
    EVERYTHING = 'animations/Stand/Gestures/Everything_1'  # thorough
    I_DONT_KNOW = 'animations/Stand/Gestures/IDontKnow_1'  # knowledgeable


class AutonomousLife(ESEnum):
    SOLITARY = "solitary"
    INTERACTIVE = "interactive"
    DISABLED = "disabled"


class HeadMotion(ESEnum):
    YAW = ('HeadYaw', [-2.0857, 2.0857])
    PITCH = ('HeadPitch', [-0.7068, 0.4451])

    def __init__(self, _name, _range):
        self._name = _name
        self._range = _range


class MovingStatus(ESEnum):
    ENTERING = 1
    EXITING = -1
    UNKNOWN = 0


class MovingDirection(ESEnum):
    FORWARD = 1
    BACKWARD = -1
    STAND_STILL = 0


class MovingOrientation(ESEnum):
    RIGHT = 1
    LEFT = -1
    CENTER = 0
