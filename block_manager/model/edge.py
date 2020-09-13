from collections import OrderedDict

from block_manager.enums.block_enums import EdgeType
from block_manager.view.graphics_edge import *
from es_common.datasource.serializable import Serializable
from es_common.model.observable import Observable

import logging


class Edge(Serializable, Observable):
    def __init__(self, scene, start_socket, end_socket=None, edge_type=EdgeType.BEZIER):
        super(Edge, self).__init__()
        Observable.__init__(self)  # explicit call to second parent class

        self.logger = logging.getLogger("Edge")

        self.scene = scene

        # init sockets
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.graphics_edge, self.__edge_type = (None,) * 2
        self.edge_type = edge_type

        # add edge to the scene
        self.scene.add_edge(self)

    def __str__(self):
        return "<Edge id {}..{}>".format((hex(id(self))[2:5]), (hex(id(self))[-3:]))

    def update_destination(self, x, y):
        self.graphics_edge.set_destination(x, y)
        self.update_path()

    def update_path(self):
        self.graphics_edge.update_path()

    def _update_graphics_edge(self):
        if hasattr(self, "graphics_edge") and self.graphics_edge is not None:
            self.scene.graphics_scene.removeItem(self.graphics_edge)

        if self.edge_type is EdgeType.DIRECT:
            self.graphics_edge = ESGraphicsEdgeDirect(self)
        else:  # EdgeType.BEZIER
            self.graphics_edge = ESGraphicsEdgeBezier(self)

        self.scene.graphics_scene.addItem(self.graphics_edge)

        self.update_positions()

    def update_positions(self):
        # in case the edge has no starting point, return
        if self.start_socket is None:
            return

        s_pos = self.start_socket.get_socket_position()
        # add pos x and y
        s_pos[0] += self.start_socket.block.get_pos().x()
        s_pos[1] += self.start_socket.block.get_pos().y()
        self.graphics_edge.set_source(*s_pos)

        if self.end_socket is not None:
            d_pos = self.end_socket.get_socket_position()
            d_pos[0] += self.end_socket.block.get_pos().x()
            d_pos[1] += self.end_socket.block.get_pos().y()
            self.graphics_edge.set_destination(*d_pos)
        else:
            self.graphics_edge.set_destination(*s_pos)

        # this was useful for preventing the path from being invisible in the scene
        # it will update the edge path which will notify the paint functionality
        self.graphics_edge.update_path()
        self.graphics_edge.update()

    @property
    def start_socket(self):
        return self.__start_socket

    @start_socket.setter
    def start_socket(self, value):
        self.__start_socket = value
        self.connect_socket(self.start_socket)

    @property
    def end_socket(self):
        return self.__end_socket

    @end_socket.setter
    def end_socket(self, value):
        self.__end_socket = value
        self.connect_socket(self.end_socket)

    @property
    def edge_type(self):
        return self.__edge_type

    @edge_type.setter
    def edge_type(self, value):
        self.__edge_type = value
        self._update_graphics_edge()

    def set_selected(self, val=False):
        self.graphics_edge.setSelected(val)

    def get_connected_blocks(self):
        if self.start_socket is None:
            return []
        elif self.end_socket is None:
            return [self.start_socket.block]

        return [self.start_socket.block, self.end_socket.block]

    def connect_socket(self, socket):
        if socket is not None:
            socket.add_edge(self)

    def disconnect_sockets(self):
        if self.start_socket is not None:
            self.start_socket.remove_edge(self)
        self.start_socket = None

        if self.end_socket is not None:
            self.end_socket.remove_edge(self)
        self.end_socket = None

    def remove_from_scene(self):
        self.scene.remove_edge(self)

    def remove(self):
        try:
            self.remove_from_scene()
            self.disconnect_sockets()
            self.logger.debug("Removed edge {} connecting {} <--> {}".format(self, self.start_socket, self.end_socket))
        except Exception as e:
            self.logger.error("ERROR while removing edge {} | {}".format(self, e))

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("edge_type", self.edge_type.name),
            ("start_socket", self.start_socket.id),
            ("end_socket", self.end_socket.id)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        # start_socket is already passed as parameter on init
        # self.end_socket = hashmap[data["end_socket"]]

        # self.edge_type = EdgeType[data["edge_type"]]

        return True
