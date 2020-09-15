#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ==================== #
# ESBLOCK_CONTROLLER #
# ==================== #
# Class for controlling the interactions blocks.
#
# @author ES
# **

import logging

from PyQt5 import QtCore, QtGui

from block_manager.controller.block_controller import BlockController
from block_manager.model.block import Block
from es_common.utils import block_helper
from interaction_manager.controller.block_list_controller import ESBlockListWidget
from es_common.model.interaction_block import InteractionBlock
from interaction_manager.utils import config_helper


class ESBlockController(BlockController):
    def __init__(self, parent_widget=None):
        super(ESBlockController, self).__init__(parent_widget)

        self.logger = logging.getLogger("ESBlock Controller")
        self.block_list_widget = ESBlockListWidget()

        # observe when new blocks are created from undo/redo operations
        block_helper.block_observable.add_observer(self.update_block_selected_observer)

        self.hidden_scene = None

    def update_block_selected_observer(self, block):
        if type(block) is Block:
            # disable settings icon
            block.content.settings_icon.setEnabled(False)
            super(ESBlockController, self).update_block_selected_observer(block=block)

    def on_drop(self, event):
        # self.logger.debug("Drop event: {}".format(event.mimeData().text()))
        if event.mimeData().hasFormat(self.get_block_mime_type()):
            # clear selection
            self.scene.clear_selection()

            event_data = event.mimeData().data(self.get_block_mime_type())
            data_stream = QtCore.QDataStream(event_data, QtCore.QIODevice.ReadOnly)

            item_pixmap = QtGui.QPixmap()
            data_stream >> item_pixmap
            op_code = data_stream.readInt()
            item_text = data_stream.readQString()

            # check if the block has a "start" pattern and the scene already contains one:
            start_block = self.get_block(pattern="start")
            if "start" == item_text.lower() and start_block is not None:
                to_display = "The scene has already a start block! The drop is ignored."
                self.logger.warning(to_display)
                start_block.set_selected(True)
                self.start_block_observable.notify_all(to_display)
                event.ignore()
            else:
                mouse_position = event.pos()
                scene_position = self.get_scene_position(mouse_position)

                self.logger.debug("Item with: {} | {} | mouse: {} | scene pos: {}".format(op_code, item_text,
                                                                                          mouse_position,
                                                                                          scene_position))
                # new interaction block
                self.create_interaction_block(title=item_text,
                                              pos=[scene_position.x(), scene_position.y()],
                                              pattern=item_text.lower())
                # self.add_block(title=item_text, num_inputs=2, num_outputs=1,
                #                                pos=[scene_position.x(), scene_position.y()],
                #                                observer=self.block_is_selected)
                self.store("Added new {}".format(item_text))

                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
        else:
            self.logger.debug("*** drop ignored")
            event.ignore()

    def create_interaction_block(self, title, pos, pattern):
        num_inputs, num_outputs, output_edges = 0, 1, 1
        icon, bg_color = (None,) * 2

        patterns = config_helper.get_patterns()
        if pattern is not None and pattern.lower() in patterns:
            num_inputs = patterns[pattern.lower()]["inputs"]
            num_outputs = patterns[pattern.lower()]["outputs"]
            output_edges = patterns[pattern.lower()]["output_edges"]
            icon = patterns[pattern.lower()]["icon"]
            bg_color = patterns[pattern.lower()]["bg_color"] if "bg_color" in patterns[pattern.lower()].keys() else None
        else:
            pattern = "start"

        # TODO: create block from pattern
        interaction_block = InteractionBlock(name=title, pattern=pattern)
        interaction_block.block = self.add_block(title=title,
                                                 num_in=num_inputs, num_out=num_outputs,
                                                 pos=pos,
                                                 observer=self.block_is_selected,
                                                 parent=interaction_block,
                                                 icon=icon,
                                                 output_edges=output_edges,
                                                 bg_color=bg_color)
        # editing/settings observers
        interaction_block.block.settings_observers.add_observer(self.block_settings_selected)
        interaction_block.block.editing_observers.add_observer(self.block_editing_selected)

        # disable settings icon
        interaction_block.block.content.settings_icon.setEnabled(False)

        return interaction_block

    def get_hidden_block(self, pattern=None):
        if pattern is None or self.hidden_scene is None:
            return None

        for block in self.get_hidden_blocks():
            if block.pattern.lower() == pattern.lower():
                return block
        return None

    def get_hidden_blocks(self):
        return None if self.hidden_scene is None else self.hidden_scene.blocks
