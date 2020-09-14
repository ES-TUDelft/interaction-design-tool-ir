#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# COMMAND_ENUMS #
# ============ #
# List of enums for the command
#
# @author ES
# **

from es_common.enums.es_enum import ESEnum


class ActionCommand(ESEnum):
    PLAY_MUSIC = "PlayMusic"
    GET_RESERVATIONS = "GetReservations"
    CHECK_RESERVATIONS = "CheckReservations"
    WAIT = "Wait"
