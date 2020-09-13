# !/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# TABLET_ENUMS #
# ============ #
# List of enums needed for controlling the tablet
#
# @author ES
# **

from __future__ import absolute_import
from es_common.enums.es_enum import ESEnum


class HtmlPage(ESEnum):
    GREETINGS = "Greetings"
    HOME = "Index"
    SURVEY = "Survey"


class TabletAction(ESEnum):
    IMAGE = 'Image'
    WEBVIEW = 'Webview'
