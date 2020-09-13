import logging
from collections import OrderedDict

from block_manager.controller.scene_history_controller import SceneHistoryController
from block_manager.model.block import Block
from block_manager.model.edge import Edge
from block_manager.view.graphics_scene import ESGraphicsScene
from es_common.datasource.serializable import Serializable
from es_common.model.observable import Observable
from es_common.utils import data_helper


class Scene(Serializable, Observable):
    def __init__(self):
        super(Scene, self).__init__()
        Observable.__init__(self)

        self.logger = logging.getLogger("Scene")

        self.blocks = []
        self.edges = []

        self.graphics_scene = ESGraphicsScene(self)

        self.history = SceneHistoryController(self)

    def set_scene_rect(self, width, height):
        self.graphics_scene.set_scene_rect(width, height)

    def clear_selection(self):
        self.graphics_scene.clearSelection()

    def add_block(self, block):
        self.blocks.append(block)
        self.graphics_scene.addItem(block.graphics_block)
        self.logger.debug("Added block '{}': {}".format(block.title, block))

    def remove_block(self, block):
        self.graphics_scene.removeItem(block.graphics_block)
        self.blocks.remove(block)
        self.logger.debug("Removed block '{}: {}".format(block.title, block))

    # Edges
    def add_edge(self, edge):
        self.edges.append(edge)
        self.graphics_scene.addItem(edge.graphics_edge)
        self.logger.debug("Added edge to scene '{}: {} | {}".format(edge, edge.start_socket, edge.end_socket))

    def remove_edge(self, edge):
        self.edges.remove(edge)
        self.graphics_scene.removeItem(edge.graphics_edge)
        self.logger.debug("Removed edge from scene '{}: {} | {}".format(edge, edge.start_socket, edge.end_socket))

    def store(self, description):
        success = self.history.store(description)
        if success is True:
            self.notify_all("Stored scene")

    def save_scene(self, filename):
        try:
            data_helper.save_to_file(filename, self.serialize())
        except Exception as e:
            self.logger.error("Error while saving scene data to: {} | {}".format(filename, e))
            return False

    def load_scene(self, filename):
        scene_data = data_helper.load_data_from_file(filename)
        return self.load_scene_data(scene_data)

    def load_scene_data(self, data):
        try:
            self.deserialize(data)
            return True
        except Exception as e:
            self.logger.error("Error while loading scene data: {} | {}".format(data, e))
            return False

    def clear(self):
        for edge in self.edges:
            edge.remove()
            edge = None
        for block in self.blocks:
            block.remove()
            block = None

        self.graphics_scene.clear()

        self.edges = []
        self.blocks = []

    def undo(self):
        self.history.undo()
        self.update_edges()
        self.notify_all("Undo Scene")

    def redo(self):
        self.history.redo()
        self.update_edges()
        self.notify_all("Redo Scene")

    def update_edges(self):
        for e in self.edges:
            e.update_path()

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        to_return = OrderedDict([
            ("id", self.id),
            ("blocks", []),
            ("edges", [])
        ])

        try:
            # serialize the blocks
            to_return["blocks"] = [b.serialize() for b in self.blocks]

            # serialize the edges
            serialized_edges = []
            for e in self.edges:
                if e.start_socket is not None and e.end_socket is not None:
                    serialized_edges.append(e.serialize())
            to_return["edges"] = serialized_edges

        except Exception as e:
            self.logger.error("Error while serializing the scene! {}".format(e))
        finally:
            return to_return

    def deserialize(self, data, hashmap=None):
        try:
            # clear scene
            self.clear()

            hashmap = {}

            # create block
            for b_data in data["blocks"]:
                Block(self, bg_color=self.get_property(b_data, "bg_color")).deserialize(b_data, hashmap)

            # create edges
            for e_data in data["edges"]:
                Edge(scene=self,
                     start_socket=hashmap[e_data["start_socket"]],
                     end_socket=hashmap[e_data["end_socket"]]
                     ).deserialize(e_data, hashmap)
            return True
        except Exception as e:
            self.logger.error("Error while serializing the scene! {}".format(e))
            return False
