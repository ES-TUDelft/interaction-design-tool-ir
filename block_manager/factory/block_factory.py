#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# BLOCK_FACTORY #
# =========== #
# Factory for creating scene elements (blocks and edges).
#
# @author ES
# **

from block_manager.enums.block_enums import SocketType, EdgeType
from block_manager.model.edge import Edge
from block_manager.model.block import Block
from block_manager.model.scene import Scene
from block_manager.view.block_manager_widget import BlockManagerWidget


class BlockFactory(object):

    @staticmethod
    def create_scene():
        return Scene()

    @staticmethod
    def create_block_widget(scene, parent=None):
        return BlockManagerWidget(scene=scene, parent=parent)

    @staticmethod
    def create_block(scene, title, num_in, num_out, pos, observer=None,
                     parent=None, icon=None, output_edges=1, bg_color=None):
        inputs = [SocketType.INPUT] * num_in
        outputs = [SocketType.OUTPUT] * num_out
        new_pos = [] if pos is None or len(pos) < 2 else pos  # needs to be [x, y]

        b = Block(scene=scene, title=title, socket_types=(inputs + outputs),
                  pos=new_pos, parent=parent, icon=icon, output_edges=output_edges, bg_color=bg_color)
        if observer is not None:
            b.add_observer(observer)

        return b

    @staticmethod
    def create_edge(scene, start_socket, end_socket, edge_type=EdgeType.BEZIER):
        return Edge(scene, start_socket, end_socket, edge_type)
