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
    GET_RESERVATIONS = "GetReservations"
    PLAY_MUSIC = "PlayMusic"
    WAIT = "Wait"
