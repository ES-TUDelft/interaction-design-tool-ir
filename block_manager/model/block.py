import logging
from collections import OrderedDict

from block_manager.enums.block_enums import Position, SocketType
from block_manager.model.socket import Socket
from block_manager.view.block_content_widget import ESBlockContentWidget
from block_manager.view.graphics_block import ESGraphicsBlock
from es_common.datasource.serializable import Serializable
from es_common.model.observable import Observable
from es_common.utils import block_helper


class Block(Serializable, Observable):

    def __init__(self, scene, title="Start", socket_types=[], pos=[],
                 parent=None, icon=None, output_edges=1, bg_color=None):
        super(Block, self).__init__()
        Observable.__init__(self)  # explicit call to second parent class

        self.logger = logging.getLogger("Block")

        self.scene = scene
        self.parent = parent  # any container
        self.graphics_block = None
        self.bg_color = bg_color

        self.icon = icon
        self.title = title  # is also the pattern name

        self.inputs = []
        self.outputs = []

        self.socket_spacing = 22

        self._init_ui(socket_types, pos, output_edges)

        # add observers
        self.editing_observers = Observable()
        self.settings_observers = Observable()

        # add editing/settings listeners
        self.content.editing_icon.clicked.connect(lambda: self.editing_observers.notify_all(event=self))
        self.content.settings_icon.clicked.connect(lambda: self.settings_observers.notify_all(event=self))

        # add block to the scene
        self.scene.add_block(self)

    def _init_ui(self, socket_types, pos, output_edges):
        self.content = ESBlockContentWidget(block=self)
        self.graphics_block = ESGraphicsBlock(block=self, bg_color=self.bg_color)

        self._init_sockets(socket_types, output_edges)

        if pos is not None and len(pos) == 2:
            self.set_pos(*pos)

    def _init_sockets(self, socket_types, output_edges):
        in_counter = 0
        out_counter = 0
        for st in socket_types:
            if st is SocketType.INPUT:
                self.inputs.append(Socket(block=self,
                                          index=in_counter,
                                          position=Position.BOTTOM_LEFT,
                                          socket_type=SocketType.INPUT))
                in_counter += 1
            else:
                self.outputs.append(Socket(block=self,
                                           index=out_counter,
                                           position=Position.TOP_RIGHT,
                                           socket_type=SocketType.OUTPUT,
                                           edge_limit=output_edges)
                                    )
                out_counter += 1

    def get_socket_position(self, index, position):
        # set x
        x, y = 0, 0  # for the left side
        try:
            if position in (Position.TOP_RIGHT, Position.BOTTOM_RIGHT, Position.CENTER_RIGHT):
                x = self.graphics_block.width

            # set y
            if position in (Position.CENTER_LEFT, Position.CENTER_RIGHT):
                y = (self.graphics_block.height / 2) - index * self.socket_spacing
            elif position in (Position.BOTTOM_LEFT, Position.BOTTOM_RIGHT):
                # start on bottom
                y = self.graphics_block.height - (2 * self.graphics_block.rounded_edge_size) - index * self.socket_spacing
            else:
                y = self.graphics_block.title_height + self.graphics_block.rounded_edge_size + index * self.socket_spacing
        except Exception as e:
            self.logger.debug("Error while getting the socket position! {}".format(e))
        finally:
            return [x, y]

    def update_connected_edges(self):
        for socket in self.inputs + self.outputs:
            socket.update_edge_positions()

    def is_connected_to(self, other_block):
        """
        :param other_block:
        :return: True if two blocks are connected; False otherwise.
        """
        for edge in self.scene.edges:
            if self in (edge.start_socket.block, edge.end_socket.block) and \
                    other_block in (edge.start_socket.block, edge.end_socket.block):
                self.logger.info("{} is connected to {}".format(self, other_block))
                return True

        return False

    def get_edges(self, socket_type=SocketType.OUTPUT):
        edges = []
        for s in (self.outputs if socket_type is SocketType.OUTPUT else self.inputs):
            edges.extend([e for e in s.edges])
        return edges

    def get_connected_blocks(self, socket_type=SocketType.OUTPUT):
        blocks = []
        # go through target sockets and get the connected blocks
        for output_socket in (self.outputs if socket_type is SocketType.OUTPUT else self.inputs):
            connected_sockets = output_socket.get_connected_sockets()
            if connected_sockets is not None:
                blocks.extend([s.block for s in connected_sockets])

        self.logger.debug("# of Connected blocks: {}".format(0 if blocks is None else len(blocks)))
        return blocks

    def remove(self):
        # remove socket edges
        for socket in (self.inputs + self.outputs):
            # remove edges, if any
            socket.disconnect_all_edges()

        # remove block from scene
        self.scene.remove_block(self)
        self.graphics_block = None

    def __str__(self):
        return "<Block id {}..{}>".format((hex(id(self))[2:5]), (hex(id(self))[-3:]))

    def get_pos(self):
        return self.graphics_block.pos()  # QPointF

    def set_pos(self, x, y):
        self.graphics_block.setPos(x, y)

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value
        if self.graphics_block is not None:
            self.graphics_block.title = self.title

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, value):
        self.__icon = value
        if self.graphics_block is not None:
            self.graphics_block.set_title_pixmap(self.icon)

    @property
    def description(self):
        return self.content.description

    @description.setter
    def description(self, desc):
        self.content.description = desc

    def set_selected(self, val):
        if val is not None and self.graphics_block is not None:
            self.graphics_block.setSelected(val)

    @property
    def pattern(self):
        return self.parent.pattern if self.parent is not None else self.title

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("title", self.title),
            ("icon", self.icon),
            ("pos_x", self.graphics_block.scenePos().x()),
            ("pos_y", self.graphics_block.scenePos().y()),
            ("inputs", [s.serialize() for s in self.inputs]),
            ("outputs", [s.serialize() for s in self.outputs]),
            ("content", self.content.serialize()),
            ("parent", {} if self.parent is None else self.parent.serialize()),
            ("bg_color", self.bg_color)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        self.icon = data["icon"]
        self.title = data["title"]
        self.set_pos(data["pos_x"], data["pos_y"])
        self.bg_color = data["bg_color"] if "bg_color" in data.keys() else None

        # set inputs and outputs
        data["inputs"].sort(key=lambda s: s["index"] + Position[s["position"]].value * 1000)
        data["outputs"].sort(key=lambda s: s["index"] + Position[s["position"]].value * 1000)

        self.inputs = []
        for s_data in data["inputs"]:
            socket = Socket(block=self,
                            index=s_data["index"],
                            position=Position[s_data["position"]],
                            socket_type=SocketType[s_data["socket_type"]],
                            edge_limit=s_data["edge_limit"] if "edge_limit" in s_data.keys() else 1)
            socket.deserialize(s_data, hashmap)
            self.inputs.append(socket)

        self.outputs = []
        for s_data in data["outputs"]:
            socket = Socket(block=self,
                            index=s_data["index"],
                            position=Position[s_data["position"]],
                            socket_type=SocketType[s_data["socket_type"]],
                            edge_limit=s_data["edge_limit"] if "edge_limit" in s_data.keys() else 1)
            socket.deserialize(s_data, hashmap)
            self.outputs.append(socket)

        self.content.deserialize(data["content"], hashmap)

        # set parent
        if "parent" in data.keys() and len(data["parent"]) > 0:
            self.parent = block_helper.create_block_parent(data["parent"], hashmap)

        return True
