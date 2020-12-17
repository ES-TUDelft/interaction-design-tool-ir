#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# INTERACTION_ENUMS #
# ================= #
#
# @author ES
# **

from es_common.enums.es_enum import ESEnum


class CommunicationStyle(ESEnum):
    UNDEFINED = "Undefined"
    TASK_ORIENTED = "TaskOriented"
    PERSON_ORIENTED = "PersonOriented"
