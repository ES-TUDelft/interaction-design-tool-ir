#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ==================== #
# BLOCK_CONTROLLER #
# ==================== #
# Class for controlling the interactions blocks.
#
# @author ES
# **

import logging

from es_common.utils.qt import QtWidgets, QtCore, QtGui

from block_manager.controller.block_list_controller import BlockListWidget
from block_manager.enums.block_enums import EdgeType
from block_manager.factory.block_factory import BlockFactory
from block_manager.model.block import Block
from block_manager.utils import config_helper
from es_common.model.observable import Observable


class BlockController(object):
    def __init__(self, parent_widget=None):
        self.logger = logging.getLogger("AppBlock Controller")

        self.scene = BlockFactory.create_scene()
        self.scene.add_observer(self.on_scene_change)

        # widgets
        self.block_list_widget = BlockListWidget()
        self.block_widget = BlockFactory.create_block_widget(scene=self.scene, parent=parent_widget)
        # Add observers
        self.block_widget.drag_enter_observers.add_observer(self.on_drag_enter)
        self.block_widget.drop_observers.add_observer(self.on_drop)
        self.block_widget.block_selected_observers.add_observer(self.on_block_selected)
        self.block_widget.no_block_selected_observers.add_observer(self.on_no_block_selected)
        self.block_widget.right_click_block_observers.add_observer(self.on_right_click_block)
        self.block_widget.invalid_edge_observers.add_observer(self.on_invalid_edge)

        # Observables
        self.block_selected_observers = Observable()
        self.no_block_selected_observers = Observable()
        self.block_settings_observers = Observable()
        self.block_editing_observers = Observable()
        self.start_block_observers = Observable()
        self.right_click_block_observers = Observable()
        self.invalid_edge_observers = Observable()
        self.scene_change_observers = Observable()

        # store initial state
        self.store("Initial Scene")

    def create_block_dock(self, floating=False):
        blocks_dock = QtWidgets.QDockWidget("Blocks")
        blocks_dock.setWidget(self.block_list_widget)
        blocks_dock.setFloating(floating)

        return blocks_dock

    def on_drag_enter(self, event):
        self.logger.debug("Drag entered: {}".format(event.mimeData().text()))
        if event.mimeData().hasFormat(self.get_block_mime_type()):
            # accept drop
            event.acceptProposedAction()
        else:
            # deny drop
            event.setAccepted(False)

    def on_drop(self, event):
        """
        On Drop will be overridden in the classes that extend BlockManager
        :param event:
        :return:
        """
        # self.logger.debug("Drop event: {}".format(event.mimeData().text()))
        if event.mimeData().hasFormat(self.get_block_mime_type()):
            # clear selection
            self.scene.clear_selection()

            event_data = event.mimeData().data(self.get_block_mime_type())
            data_stream = QtCore.QDataStream(event_data, QtCore.QIODevice.ReadOnly)

            item_pixmap = QtGui.QPixmap()
            data_stream >> item_pixmap

            try:
                op_code = data_stream.readInt()
            except Exception as e:
                self.logger.warning("'readInt' does not exist in QDataStream, using readInt64 instead. | {}".format(e))
                op_code = data_stream.readInt64()

            item_text = data_stream.readQString()

            mouse_position = event.pos()
            scene_position = self.get_scene_position(mouse_position)

            self.logger.debug("Item with: {} | {} | mouse: {} | scene pos: {}".format(op_code, item_text,
                                                                                      mouse_position,
                                                                                      scene_position))

            block = self.add_block(title=item_text,
                                   num_in=1, num_out=1,
                                   pos=[scene_position.x(), scene_position.y()],
                                   observer=self.on_block_selected,
                                   parent=None,
                                   icon=item_text.lower())
            # editing/settings observers
            block.settings_observers.add_observer(self.on_block_settings)
            block.editing_observers.add_observer(self.on_block_editing)

            self.store("Added new {}".format(item_text))

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            self.logger.debug("*** drop ignored")
            event.ignore()

    def update_block_selected_observer(self, block):
        if type(block) is Block:
            self.logger.debug("Observer for {} is updated.".format(block.title))
            block.add_observer(self.on_block_selected)
            block.settings_observers.add_observer(self.on_block_settings)
            block.editing_observers.add_observer(self.on_block_editing)

    def update_all_blocks_selected_observer(self):
        for block in self.get_blocks():
            self.logger.debug("Observer for {} is updated.".format(block.title))
            block.add_observer(self.on_block_selected)
            # editing/settings observers
            block.settings_observers.add_observer(self.on_block_settings)
            block.editing_observers.add_observer(self.on_block_editing)

    def on_block_selected(self, block):
        if type(block) is Block:
            self.logger.debug("Block '{}' is selected. | id = {}".format(block.title, block.id))

            self.update()
            self.block_selected_observers.notify_all(block)
        else:
            self.on_no_block_selected(block)

    def on_no_block_selected(self, event):
        self.logger.debug("No block is selected: {}".format(event))

        self.update()
        self.no_block_selected_observers.notify_all(event)

    def on_block_settings(self, block):
        if type(block) is Block:
            self.logger.debug("Settings icon of Block '{}' is selected. | id = {}".format(block.title, block.id))
            self.block_settings_observers.notify_all(block)

    def on_block_editing(self, block):
        if type(block) is Block:
            self.logger.debug("Editing icon of Block '{}' is selected. | id = {}".format(block.title, block.id))
            self.block_editing_observers.notify_all(block)

    def on_right_click_block(self, event):
        self.right_click_block_observers.notify_all(event)

    def on_invalid_edge(self, event):
        self.invalid_edge_observers.notify_all(event)

    def on_scene_change(self, event):
        self.logger.debug("Received notification for 'scene change': {}".format(event))

        self.update()
        self.scene_change_observers.notify_all(event)

    def update(self):
        self.block_widget.update()

    def get_block(self, pattern=None):
        if pattern is None:
            return None

        for block in self.get_blocks():
            if block.pattern.lower() == pattern.lower():
                return block
        return None

    def add_block(self, title, num_in, num_out, pos, observer=None,
                  parent=None, icon=None, output_edges=1, bg_color=None):
        return BlockFactory.create_block(self.scene, title, num_in, num_out, pos,
                                         observer, parent, icon, output_edges, bg_color)

    def delete_block(self, block):
        block.remove()
        self.logger.debug("Removed block")

    def add_edge(self, start_socket, end_socket, edge_type=EdgeType.BEZIER):
        return BlockFactory.create_edge(self.scene, start_socket, end_socket, edge_type)

    def delete_edge(self, edge):
        edge.remove()
        self.logger.debug("Removed edge")

    def store(self, description):
        self.scene.store(description=description)

    def save_blocks(self, filename):
        self.scene.save_scene(filename=filename)

    def load_blocks(self, filename):
        self.scene.load_scene(filename=filename)
        self.store("Loaded scene file")

    def load_blocks_data(self, data):
        self.scene.load_scene_data(data=data)
        self.store("Loaded scene data")

    def get_serialized_scene(self):
        return self.scene.serialize()

    def get_scene_position(self, mouse_position):
        return self.block_widget.get_scene_position(mouse_position)

    def get_item_at(self, pos):
        return self.block_widget.get_item_at(pos)

    def get_blocks(self):
        return self.scene.blocks

    def get_block_mime_type(self):
        return config_helper.get_block_mimetype()

    def get_parent_blocks(self):
        blocks = self.scene.blocks

        return None if blocks is None else [b.parent for b in blocks]

    def get_edges(self):
        return self.scene.edges

    def zoom_scene(self, val):
        self.block_widget.zoom_scene(val=val)

    def clear_scene(self):
        self.scene.clear()
        self.store("Cleared scene.")

    def clear_selection(self):
        self.scene.clear_selection()

    def undo(self):
        self.scene.undo()

    def redo(self):
        self.scene.redo()

    def delete_selected(self):
        self.block_widget.delete_selected()

    def get_block_by_id(self, block_id=0):
        blocks = self.get_blocks()
        if blocks is None:
            return None

        for b in blocks:
            if b.id == block_id:
                return b
        return None

    def get_block_by_parent_id(self, parent_id=0):
        parent_blocks = self.get_parent_blocks()
        if parent_blocks is None:
            return None

        for p in parent_blocks:
            if p is not None and p.id == parent_id:
                return p
        return None

    def get_block_widget(self):
        return self.block_widget
