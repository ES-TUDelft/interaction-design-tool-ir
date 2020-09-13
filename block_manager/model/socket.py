import logging
from collections import OrderedDict

from block_manager.enums.block_enums import Position, SocketType
from block_manager.view.graphics_socket import ESGraphicsSocket
from es_common.datasource.serializable import Serializable
from es_common.model.observable import Observable


class Socket(Serializable, Observable):
    def __init__(self, block, index=0, position=Position.BOTTOM_LEFT, socket_type=SocketType.INPUT, edge_limit=-1):
        super(Socket, self).__init__()
        Observable.__init__(self)  # explicit call to second parent class

        self.logger = logging.getLogger("Socket")

        self.block = block
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.edge_limit = edge_limit

        self.edges = []
        self._init_graphics()

    def _init_graphics(self):
        # create a graphics socket and attach it to the graphics block as parent
        self.graphics_socket = ESGraphicsSocket(socket=self, parent=self.block.graphics_block)
        # set the socket's position
        self.graphics_socket.setPos(*self.block.get_socket_position(self.index, self.position))

    def __str__(self):
        return "<Socket id {}..{}>".format((hex(id(self))[2:5]), (hex(id(self))[-3:]))

    def get_socket_position(self):
        return self.block.get_socket_position(self.index, self.position)

    def add_edge(self, edge):
        if edge is None or edge in self.edges:
            return False

        self.edges.append(edge)
        return True

    def remove_edge(self, edge):
        if self.has_edge(edge):
            self.edges.remove(edge)
            return True

        return False

    def disconnect_all_edges(self):
        for edge in self.edges:
            edge.remove()
        self.edges = []

    def has_edge(self, edge):
        return edge in self.edges

    def can_have_more_edges(self):
        if self.edge_limit < 0:
            return True

        if len(self.edges) >= self.edge_limit:
            self.logger.debug("Socket {} of {} cannot have more edges.".format(self, self.block.title))
            return False

        return True

    def update_edge_positions(self):
        for edge in self.edges:
            edge.update_positions()

    def is_connected_to(self, other_socket):
        if self == other_socket:
            return False
        # check if there an edge between the sockets
        for edge in self.edges:
            if edge in other_socket.edges:
                return True

        return False

    def is_connected_to_block(self, other_block):
        """
        :param other_block:
        :return: True if there a connection between the socket and the other block;
                 False otherwise
        """
        for edge in self.edges:
            if other_block in edge.get_connected_blocks():
                return True

        return False

    def is_on_same_block_as(self, other_socket):
        return self.block == other_socket.block

    def get_connected_sockets(self):
        sockets = []
        for edge in self.edges:
            sockets.append(edge.start_socket if edge.start_socket != self else edge.end_socket)
        self.logger.debug("Found {} connected sockets and {} edges".format(len(sockets), len(self.edges)))
        return sockets

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("index", self.index),
            ("position", self.position.name),
            ("socket_type", self.socket_type.name),
            ("edge_limit", self.edge_limit)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        # index, position and type are done in the block.serialize
        # list of edges is updated in the edge.serialize

        return True
