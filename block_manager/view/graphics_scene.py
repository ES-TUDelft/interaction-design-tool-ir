import logging

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from block_manager.utils import config_helper


class ESGraphicsScene(QGraphicsScene):
    def __init__(self, scene, parent=None):
        super(ESGraphicsScene, self).__init__(parent)

        self.logger = logging.getLogger("GraphicsScene")

        self.scene = scene

        # properties
        self.grid_size = 20
        self.grid_squares = 5

        self.setItemIndexMethod(QGraphicsScene.NoIndex)  # for dynamic scenes

        block_colors = config_helper.get_colors()
        self._light_pen = QPen(QColor("#{}".format(block_colors["pen"]["light"])))
        self._dark_pen = QPen(QColor("#{}".format(block_colors["pen"]["dark"])))
        # set pen width
        self._light_pen.setWidth(1)
        self._dark_pen.setWidth(2)

        self.setBackgroundBrush(QColor("#{}".format(block_colors["brush"]["scene_bg"])))

    # override to allow drag
    def dragMoveEvent(self, event):
        pass

    def set_scene_rect(self, width, height):
        self.setSceneRect(-width // 2, -height // 2,
                          width, height)

    def drawBackground(self, painter, rect):
        super(ESGraphicsScene, self).drawBackground(painter, rect)
