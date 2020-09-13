#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# ES_GRAPHICS_VIEW_CONTROLLER #
# =========================== #
# Class for controlling the scene's graphics view.
#
# @author ES
# **

from PyQt5 import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from es_common.model.observable import Observable
from block_manager.model.edge import Edge
from block_manager.view.graphics_edge import ESGraphicsEdge
from block_manager.view.graphics_socket import ESGraphicsSocket
from block_manager.enums.block_enums import Mode, EdgeType
import logging


class ESGraphicsViewController(QGraphicsView):
    def __init__(self, graphics_scene, parent=None):
        super(ESGraphicsViewController, self).__init__(parent)

        self.logger = logging.getLogger("GraphicsView")

        self.graphics_scene = graphics_scene

        self._init_ui()
        self.setScene(self.graphics_scene)

        self.mode = Mode.NO_OP  # no operation

        self.zoom_in_factor = 1.1
        self.zoom_clamp = True
        self.zoom = 0
        self.zoom_step = 1
        self.zoom_range = [-20, 1]

        self.drag_edge = None
        self.drag_start_socket = None

        # to deal with event observers
        self.drag_enter_observable = Observable()
        self.drop_observable = Observable()
        self.block_selected_observable = Observable()
        self.no_block_selected_observable = Observable()
        self.invalid_edge_observable = Observable()

    def _init_ui(self):
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # enable drop
        self.setAcceptDrops(True)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected()
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.graphics_scene.scene.save_scene("graph.json")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.graphics_scene.scene.load_scene("graph.json")
        # elif event.key() == Qt.Key_Z \
        #        and event.modifiers() & Qt.ControlModifier \
        #        and not event.modifiers() & Qt.ShiftModifier:
        #    self.graphics_scene.scene.history.undo()
        # elif event.key() == Qt.Key_Z \
        #        and event.modifiers() & Qt.ControlModifier \
        #        and event.modifiers() & Qt.ShiftModifier:
        #    self.graphics_scene.scene.history.redo()
        elif event.key() == Qt.Key_H:
            to_log = "\nHISTORY:\ttotal = {} -- step = {}\n".format(
                len(self.graphics_scene.scene.history.history_stack),
                self.graphics_scene.scene.history.current_step)
            index = 0
            for item in self.graphics_scene.scene.history.history_stack:
                to_log = "{}\t#{} -- {}\n".format(to_log, index, item['description'])
                index += 1
            self.logger.debug(to_log)

        super(ESGraphicsViewController, self).keyPressEvent(event)

    def dragEnterEvent(self, event):
        self.drag_enter_observable.notify_all(event)

    def dropEvent(self, event):
        self.drop_observable.notify_all(event)

    def mouseMoveEvent(self, event):
        if self.mode == Mode.DRAG_EDGE:
            pos = self.mapToScene(event.pos())
            self.drag_edge.update_destination(pos.x(), pos.y())

        super(ESGraphicsViewController, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.left_mouse_button_press(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_press(event)
        elif event.button() == Qt.MiddleButton:
            self.middle_mouse_button_press(event)
        else:
            super(ESGraphicsViewController, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.left_mouse_button_release(event)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_release(event)
        elif event.button() == Qt.MiddleButton:
            self.middle_mouse_button_release(event)
        else:
            super(ESGraphicsViewController, self).mouseReleaseEvent(event)

    def left_mouse_button_press(self, event):
        item = self.get_clicked_item(event)

        # self.logger.debug("Item {} is clicked!".format(item))
        if hasattr(item, "block"):
            # send the item not the event
            self.block_selected_observable.notify_all(event)
        else:
            self.no_block_selected_observable.notify_all(event)

        # if item is None:  # drag the scene
        #    pass  # self.setDragMode(QGraphicsView.ScrollHandDrag)
        if type(item) is ESGraphicsSocket:
            if self.mode == Mode.NO_OP:
                self.edge_drag_start(item)
                return

        if self.mode == Mode.DRAG_EDGE:
            success = self.edge_drag_end(item)
            if success:
                return

        super(ESGraphicsViewController, self).mousePressEvent(event)

    def left_mouse_button_release(self, event):
        item = self.get_clicked_item(event)

        # if item is None:
        #    pass  # self.setDragMode(QGraphicsView.NoDrag)

        if self.mode == Mode.DRAG_EDGE:
            # bypass the first click-release on the same socket
            if type(item) is ESGraphicsSocket:
                if item.socket != self.drag_start_socket:
                    success = self.edge_drag_end(item)
                    if success:
                        return

        # if item is not None and self.dragMode() == QGraphicsView.RubberBandDrag and self.mode is Mode.NO_OP:
        #    print("selection changed")
        # self.graphics_scene.scene.history.store("Selection changed")

        super(ESGraphicsViewController, self).mouseReleaseEvent(event)

    def right_mouse_button_press(self, event):
        super(ESGraphicsViewController, self).mousePressEvent(event)

        item = self.get_clicked_item(event)

        if item is None:
            # displays the number of blocks and edges in the scene
            to_log = "\nSCENE:\n\tBlocks:"
            for block in self.graphics_scene.scene.blocks:
                to_log = "{}\n\t\t{}".format(to_log, block)
            to_log = "{}\n\tEdges:".format(to_log)
            for edge in self.graphics_scene.scene.edges:
                to_log = "{}\n\t\t{}".format(to_log, edge)
            self.logger.info(to_log)
        elif isinstance(item, ESGraphicsSocket):
            self.logger.info("{} has edges: {}".format(item.socket, item.socket.edges))
        elif isinstance(item, ESGraphicsEdge):
            self.logger.debug("{} connecting {} & {}".format(item.edge,
                                                             item.edge.start_socket.block.title,
                                                             item.edge.end_socket.block.title))
            self.logger.debug("Edge is in {}: {} | in {}: {}".format(item.edge.start_socket,
                                                                     item.edge in item.edge.start_socket.edges,
                                                                     item.edge.end_socket,
                                                                     item.edge in item.edge.end_socket.edges))

    def right_mouse_button_release(self, event):
        super(ESGraphicsViewController, self).mouseReleaseEvent(event)

    def middle_mouse_button_press(self, event):
        super(ESGraphicsViewController, self).mousePressEvent(event)

    def middle_mouse_button_release(self, event):
        super(ESGraphicsViewController, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.zoom_scene(delta_y=event.angleDelta().y())
        else:
            super(ESGraphicsViewController, self).wheelEvent(event)

    def zoom_scene(self, delta_y):
        # zoom factor
        zoom_out_factor = 1 / self.zoom_in_factor

        # compute zoom
        if delta_y > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:
            self.zoom, clamped = self.zoom_range[1], True

        # scene scale
        if not clamped or self.zoom_clamp is False:
            self.scale(zoom_factor, zoom_factor)

    ###
    # Helper Methods
    ###
    def delete_selected(self):
        self.delete_selected_edges()
        self.delete_selected_blocks()

        self.graphics_scene.scene.store("Deleted selected items")

    def delete_selected_blocks(self):
        for item in self.graphics_scene.selectedItems():
            if hasattr(item, "block"):
                item.block.remove()

    def delete_selected_edges(self):
        for item in self.graphics_scene.selectedItems():
            if isinstance(item, ESGraphicsEdge):
                item.edge.remove()

    def get_clicked_item(self, event):
        pos = event.pos()
        return self.itemAt(pos)

    def edge_drag_start(self, item):
        self.mode = Mode.DRAG_EDGE

        self.drag_start_socket = item.socket

        # create a new edge with dotted line
        self.drag_edge = Edge(scene=self.graphics_scene.scene,
                              start_socket=item.socket, end_socket=None,
                              edge_type=EdgeType.BEZIER)

    def edge_drag_end(self, item):
        # update mode
        self.mode = Mode.NO_OP

        success = False
        try:
            # remove dragged edge
            self.drag_edge.remove()
            self.drag_edge = None

            if type(item) is ESGraphicsSocket:
                # check if the connection is valid
                if self.is_valid_connection(item.socket):
                    # create edge
                    Edge(scene=self.graphics_scene.scene,
                         start_socket=self.drag_start_socket,
                         end_socket=item.socket,
                         edge_type=EdgeType.BEZIER)

                    # store
                    self.graphics_scene.scene.store("New edge created")
                    success = True
        except Exception as e:
            self.logger.error("Error while ending drag! {}".format(e))
            self.invalid_edge_observable.notify_all("Error while creating the edge!")
        finally:
            return success

    def is_valid_connection(self, other_socket):
        # check if it's the same socket
        if other_socket == self.drag_start_socket:
            return False

        # connected sockets should have opposite types (input vs output)
        if other_socket.socket_type == self.drag_start_socket.socket_type:
            self.invalid_edge_observable.notify_all("* Cannot connect two sockets of the same type ({})".format(
                self.drag_start_socket.socket_type.name
            ))
            return False

        # check if one of the sockets is connected to the other's block
        if self.drag_start_socket.is_connected_to_block(other_socket.block) \
                or other_socket.is_connected_to_block(self.drag_start_socket.block):
            return False

        # check the number of allowed edges for the each block
        if not (self.drag_start_socket.can_have_more_edges() and other_socket.can_have_more_edges()):
            self.invalid_edge_observable.notify_all("* The Edge cannot be created: "
                                                    "The output has reached the max number of allowed edges!")
            return False

        # connect to a block once
        # if other_socket.block.is_connected_to(self.drag_start_socket.block):
        #    return False

        # the connection is valid
        return True
