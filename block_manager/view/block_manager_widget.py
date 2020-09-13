import logging

from PyQt5.Qt import *

from block_manager.controller.graphics_view_controller import ESGraphicsViewController
from es_common.model.observable import Observable


class BlockManagerWidget(QWidget):
    def __init__(self, scene, parent=None):
        super(BlockManagerWidget, self).__init__(parent)

        self.logger = logging.getLogger("BlockManagerWidget")

        self._init_ui(scene)

        self.right_click_block_observable = Observable()

    def _init_ui(self, scene):
        self.setGeometry(200, 200, 800, 600)

        # layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Graphics scene
        self.scene = scene

        # Graphics View
        self.blocks_view = ESGraphicsViewController(self.scene.graphics_scene, self)

        # set layout
        self.layout.addWidget(self.blocks_view)
        self.setLayout(self.layout)

        self.setWindowTitle("Block Manager")

    def contextMenuEvent(self, event):
        item = self.get_item_at(event.pos())

        if hasattr(item, "block"):
            self.logger.debug("item has block attribute: {}".format(item))
            # notify observers
            self.right_click_block_observable.notify_all(event)

        super(BlockManagerWidget, self).contextMenuEvent(event)

    def get_scene_position(self, mouse_position):
        try:
            return self.blocks_view.mapToScene(mouse_position)
        except Exception as e:
            self.logger.error("Error while mapping mouse position to scene! {}".format(e))

    def zoom_scene(self, val):
        self.blocks_view.zoom_scene(delta_y=val)

    def get_item_at(self, pos):
        return self.blocks_view.itemAt(pos)

    def delete_selected(self):
        self.blocks_view.delete_selected()

    def clean_up(self):
        # called on exit
        del self.scene
        del self.blocks_view

    ###
    # OBSERVERS
    ###
    def add_drag_enter_observer(self, observer):
        self.blocks_view.drag_enter_observable.add_observer(observer)

    def remove_drag_enter_observer(self, observer):
        return self.blocks_view.drag_enter_observable.remove_observer(observer)

    def add_drop_observer(self, observer):
        self.blocks_view.drop_observable.add_observer(observer)

    def remove_drop_observer(self, observer):
        return self.blocks_view.drop_observable.remove_observer(observer)

    def add_no_block_selected_observer(self, observer):
        self.blocks_view.no_block_selected_observable.add_observer(observer)

    def remove_no_block_selected_observer(self, observer):
        self.blocks_view.no_block_selected_observable.remove_observer(observer)

    def add_invalid_edge_observer(self, observer):
        self.blocks_view.invalid_edge_observable.add_observer(observer)

    def remove_invalid_edge_observer(self, observer):
        self.blocks_view.invalid_edge_observable.remove_observer(observer)
