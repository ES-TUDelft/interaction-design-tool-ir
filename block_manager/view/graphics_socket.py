import logging

from es_common.utils.qt import QRectF, QPen, QColor, QBrush, QGraphicsItem

from block_manager.enums.block_enums import SocketType
from block_manager.utils import config_helper


class ESGraphicsSocket(QGraphicsItem):
    def __init__(self, socket, parent=None):
        super(ESGraphicsSocket, self).__init__(parent=parent)

        self.logger = logging.getLogger("GraphicsSocket")

        self.socket = socket

        # properties
        socket_size_settings = config_helper.get_socket_size_settings()
        self.width, self.height = socket_size_settings["width"], socket_size_settings["height"]
        self.outline_width = 2.0

        block_colors = config_helper.get_colors()
        self._pen = QPen(QColor("#{}".format(block_colors['pen']['default'])))
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(QColor("#{}".format(
            block_colors['socket']['in' if self.socket.socket_type == SocketType.INPUT else 'out'])))

    def paint(self, painter, style_options, widget=None):
        # paint circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawRect(-self.width, -self.height, 2 * self.width, 2 * self.height)

    def boundingRect(self):
        return QRectF(
            -self.width - self.outline_width,
            -self.height - self.outline_width,
            2 * (self.width + self.outline_width),
            2 * (self.height + self.outline_width)
        )
