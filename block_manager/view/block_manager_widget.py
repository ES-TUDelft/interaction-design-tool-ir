import logging

from es_common.utils.qt import QWidget, QVBoxLayout

from block_manager.controller.graphics_view_controller import ESGraphicsViewController
from es_common.model.observable import Observable


class BlockManagerWidget(QWidget):
    def __init__(self, scene, parent=None):
        super(BlockManagerWidget, self).__init__(parent)

        self.logger = logging.getLogger("BlockManagerWidget")

        self._init_ui(scene)

        # Observables
        self.drag_enter_observers = Observable()
        self.drop_observers = Observable()
        self.block_selected_observers = Observable()
        self.no_block_selected_observers = Observable()
        self.invalid_edge_observers = Observable()
        self.right_click_block_observers = Observable()

    def _init_ui(self, scene):
        self.setGeometry(200, 200, 800, 600)

        # layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Graphics scene
        self.scene = scene

        # Graphics View
        self.blocks_view = ESGraphicsViewController(self.scene.graphics_scene, self)

        # add observers
        self.blocks_view.drag_enter_observers.add_observer(self.on_drag_enter)
        self.blocks_view.drop_observers.add_observer(self.on_drop)
        self.blocks_view.block_selected_observers.add_observer(self.on_block_selected)
        self.blocks_view.no_block_selected_observers.add_observer(self.on_no_block_selected)
        self.blocks_view.invalid_edge_observers.add_observer(self.on_invalid_edge)

        # set layout
        self.layout.addWidget(self.blocks_view)
        self.setLayout(self.layout)

        self.setWindowTitle("Block Manager")

        self.update_widget()
        self.show()

    def update_widget(self):
        self.update()
        # self.blocks_view.update()

    def contextMenuEvent(self, event):
        item = self.get_item_at(event.pos())

        if hasattr(item, "block"):
            self.logger.debug("item has block attribute: {}".format(item))
            # notify observers
            self.right_click_block_observers.notify_all(event)

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
    # Event Listeners
    ###
    def on_drag_enter(self, event=None):
        self.drag_enter_observers.notify_all(event)

    def on_drop(self, event=None):
        self.drop_observers.notify_all(event)

    def on_block_selected(self, event=None):
        self.block_selected_observers.notify_all(event)

    def on_no_block_selected(self, event=None):
        self.no_block_selected_observers.notify_all(event)

    def on_invalid_edge(self, event=None):
        self.invalid_edge_observers.notify_all(event)
