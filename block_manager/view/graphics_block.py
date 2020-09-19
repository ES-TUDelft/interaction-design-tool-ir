import logging

from block_manager.utils import config_helper
from es_common.model.observable import Observable
from es_common.utils.qt import QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsProxyWidget
from es_common.utils.qt import Qt, QRectF, QPen, QBrush, QColor, QPixmap, QPainterPath


class ESGraphicsBlock(QGraphicsItem, Observable, object):
    def __init__(self, block, parent=None, bg_color=None):
        super(ESGraphicsBlock, self).__init__(parent=parent)
        Observable.__init__(self)

        self.block = block
        self.logger = logging.getLogger("GraphicsBlock")

        # properties
        block_size_settings = config_helper.get_block_size_settings()
        self.width = block_size_settings["width"]
        self.height = block_size_settings["height"]
        self.rounded_edge_size = block_size_settings["rounded_edge_size"]
        self.title_height = block_size_settings["title_height"]

        self._padding = 5.0
        self.is_moved = False

        # pen
        block_colors = config_helper.get_colors()
        self._default_pen = QPen(QColor("#{}".format(block_colors['pen']['default'])))
        self._default_pen.setWidthF(2.0)
        self._selected_pen = QPen(QColor("#{}".format(block_colors['pen']['selected'])))
        self._selected_pen.setWidthF(block_size_settings["selected_pen_width"])

        self._title_brush = QBrush(QColor("#{}".format(block_colors['brush']['block_title'])))
        self._bg_brush = QBrush(QColor("#{}".format(
            block_colors['brush']['block_bg'] if bg_color is None else bg_color)))

        # set title
        self.__title = ""
        self._init_title()

        # init sockets
        self._init_sockets()

        # init content
        self._init_content()

        # init ui
        self._init_ui()

    def _init_ui(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def _init_title(self):
        # title icon

        self.title_icon = QGraphicsPixmapItem(self)
        self.title_icon.block = self.block
        self.set_title_pixmap(self.block.icon)
        self.title_icon.setPos(self._padding, 0)  # self._padding)

        # title item
        self.title_item = QGraphicsTextItem(self)
        self.title_item.block = self.block

        # self.title_item.setDefaultTextColor(Qt.white)
        self.title_item.setFont(config_helper.get_block_title_font())
        # self.title_item.setDefaultTextColor(QColor("white"))
        x_pos = self._padding + self.title_height  # self._padding + self.title_icon.pixmap().width()
        self.title_item.setPos(x_pos, 0)
        self.title_item.setTextWidth(
            self.width - 2 * self._padding
        )

        # set title
        self.title = self.block.title

    def set_title_pixmap(self, icon_path):
        if icon_path is not None:
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(self.title_height, self.title_height, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.title_icon.setPixmap(pixmap)

    def _init_sockets(self):
        pass

    def _init_content(self):
        self.content = self.block.content
        self.graphics_content = QGraphicsProxyWidget(self)
        self.graphics_content.block = self.block
        self.content.setGeometry(self.rounded_edge_size, self.title_height + self.rounded_edge_size,
                                 self.width - 2 * self.rounded_edge_size,
                                 self.height - 2 * self.rounded_edge_size - self.title_height)
        self.graphics_content.setWidget(self.content)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, "block"):
                # notify observers
                self.block.notify_all(self.block)

        super(ESGraphicsBlock, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(ESGraphicsBlock, self).mouseMoveEvent(event)

        # TODO: to be optimized --> update selected blocks
        for block in self.scene().scene.blocks:
            if block.graphics_block.isSelected():
                block.update_connected_edges()

        self.is_moved = True

    def mouseReleaseEvent(self, event):
        super(ESGraphicsBlock, self).mouseReleaseEvent(event)

        if self.is_moved:
            self.is_moved = False
            self.logger.debug("Storing history on block move.")
            self.block.scene.store("Block moved")

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value
        self.title_item.setPlainText(self.__title)

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def paint(self, painter, style_options, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.rounded_edge_size, self.rounded_edge_size)
        path_title.addRect(0, self.title_height - self.rounded_edge_size,
                           self.rounded_edge_size, self.rounded_edge_size)
        path_title.addRect(self.width - self.rounded_edge_size, self.title_height - self.rounded_edge_size,
                           self.rounded_edge_size, self.rounded_edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._title_brush)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height,
                                    self.rounded_edge_size, self.rounded_edge_size)
        path_content.addRect(0, self.title_height, self.rounded_edge_size, self.rounded_edge_size)
        path_content.addRect(self.width - self.rounded_edge_size, self.title_height,
                             self.rounded_edge_size, self.rounded_edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._bg_brush)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height,
                                    self.rounded_edge_size, self.rounded_edge_size)
        painter.setPen(self._default_pen if not self.isSelected() else self._selected_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())
