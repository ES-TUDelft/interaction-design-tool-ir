#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# BLOCK_ENUMS #
# ============ #
# List of enums for the blocks
#
# @author ES
# **

from es_common.enums.es_enum import ESEnum


class Mode(ESEnum):
    NO_OP = 1
    DRAG_EDGE = 2


class Position(ESEnum):
    TOP_LEFT = 1
    BOTTOM_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_RIGHT = 4
    CENTER_LEFT = 5
    CENTER_RIGHT = 6


class EdgeType(ESEnum):
    DIRECT = 1
    BEZIER = 2


class SocketType(ESEnum):
    INPUT = 0
    OUTPUT = 1


class ExecutionMode(ESEnum):
    NEW = 0
    EXECUTING = 1
    COMPLETED = 2
