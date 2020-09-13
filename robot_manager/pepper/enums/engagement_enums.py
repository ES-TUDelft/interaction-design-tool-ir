#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================ #
# ENGAGEMENT_ENUMS #
# ================ #
# List of enums needed for HRE
#
# @author ES
# **

from es_common.enums.es_enum import ESEnum

"""
KEY = name
VALUE = value
"""


class EngagementMode(ESEnum):
    UNENGAGED = "Unengaged"
    FULLY_ENGAGED = "FullyEngaged"
    SEMI_ENGAGED = "SemiEngaged"


class EngagementZone(ESEnum):
    ZONE1 = "EngagementZones/PeopleInZone1"
    ZONE2 = "EngagementZones/PeopleInZone2"
    ZONE3 = "EngagementZones/PeopleInZone3"


class DialogTopic(ESEnum):
    INDEX = "/home/nao/.local/share/PackageManager/apps/hre_dialog/topics/index.top"
    CHITCHAT = "/home/nao/.local/share/PackageManager/apps/hre_dialog/topics/chitchat.top"
    QUESTION = "/home/nao/.local/share/PackageManager/apps/hre_dialog/topics/question.top"
