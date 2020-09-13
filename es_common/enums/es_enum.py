#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========= #
# ESEnum #
# ========= #
# Extends Enum
#
# @author ES
# **

from enum import Enum


class ESEnum(Enum):
    """
    Extends Enum by adding two class methods:
        - keys: @return all keys
        - values: @return all values
    cls = enum class
    """

    @classmethod
    def keys(cls):
        return [elt.name for elt in cls]  # list(map(lambda elt: elt.name, cls))

    @classmethod
    def values(cls):
        return [elt.value for elt in cls]
