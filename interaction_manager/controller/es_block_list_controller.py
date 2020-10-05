#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ==================== #
# ES_BLOCK_LIST_WIDGET #
# ==================== #
# Class for controlling the drag-list of block.
#
# @author ES
# **

import logging

from block_manager.controller.block_list_controller import BlockListWidget
from interaction_manager.utils import config_helper


class ESBlockListWidget(BlockListWidget):
    def __init__(self, parent=None):
        super(ESBlockListWidget, self).__init__(parent)

        self.logger = logging.getLogger("ESBlockList Widget")

    def add_block_items(self):
        patterns = config_helper.get_patterns()

        # set the pattern order in the list
        # start block
        self.add_block_item("Start", patterns["start"]["icon"])

        for pattern in patterns:
            # get the item icon
            if pattern not in ("start", "end"):
                icon = patterns[pattern]["icon"]
                self.add_block_item(pattern.title(), icon)

        # end block
        self.add_block_item("End", patterns["end"]["icon"])

    def get_item_icon(self, item_text):
        patterns = config_helper.get_patterns()
        return patterns["{}".format(item_text).lower()]["icon"]
