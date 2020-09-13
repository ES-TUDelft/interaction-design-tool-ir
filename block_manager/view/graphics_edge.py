import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from block_manager.utils import config_helper
from block_manager.enums.block_enums import Position
import logging


class ESGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super(ESGraphicsEdge, self).__init__(parent)

        self.logger = logging.getLogger("GraphicsEdge")

        self.edge = edge

        # pen
        block_colors = config_helper.get_colors()
        self._pen = QPen(QColor("#{}".format(block_colors['pen']['edge'])))
        self._pen.setWidth(2)
        self._selected_pen = QPen(QColor("#{}".format(block_colors['pen']['edge_selected'])))
        self._selected_pen.setWidthF(4.0)
        self._dragging_pen = QPen(QColor("#{}".format(block_colors['pen']['edge'])))
        self._dragging_pen.setStyle(Qt.DashLine)
        self._dragging_pen.setWidthF(3.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        # z value: make the edge appear behind the block
        self.setZValue(-1)

        self.pos_source = [0, 0]
        self.pos_destination = [10, 30]
        self.pos_counter = 0

    def boundingRect(self):
        return self.shape().boundingRect()

    # TODO: this was causing segmentation errors!
    # def shape(self):
    #     return self.compute_path()

    def paint(self, painter, option, widget=None):
        self.update_path()

        painter.setBrush(Qt.NoBrush)

        if self.edge.end_socket is None:
            painter.setPen(self._dragging_pen)
        else:
            painter.setPen(self._selected_pen if self.isSelected() else self._pen)

        painter.drawPath(self.path())

    def update_path(self):
        # updates path from A to B
        path = self.compute_path()
        self.setPath(path)

    def compute_path(self):
        # computes and returns path from A to B
        raise NotImplemented("Abstract method")

    def set_source(self, x, y):
        self.pos_source = [x, y]

    def set_destination(self, x, y):
        self.pos_destination = [x, y]


class ESGraphicsEdgeDirect(ESGraphicsEdge):
    def compute_path(self):
        path = QPainterPath(QPointF(self.pos_source[0], self.pos_source[1]))
        path.lineTo(self.pos_destination[0], self.pos_destination[1])

        return path


class ESGraphicsEdgeBezier(ESGraphicsEdge):
    def compute_path(self):
        try:
            control_source, control_dest = self._get_control_points()

            path = QPainterPath(QPointF(self.pos_source[0], self.pos_source[1]))
            path.cubicTo(
                self.pos_source[0] + control_source[0], self.pos_source[1] + control_source[1],  # control points
                self.pos_destination[0] + control_dest[0], self.pos_destination[1] + control_dest[1],  # control points
                self.pos_destination[0], self.pos_destination[1])

            return path
        except Exception as e:
            self.logger.error("ERROR while computing edge path! {}".format(e))

    def _get_control_points(self):
        s0 = self.pos_source[0]
        d0 = self.pos_destination[0]
        distance = (d0 - s0) / 2.0

        control_source = [distance, 0]
        control_dest = [-distance, 0]

        if self.edge.start_socket is not None:
            # reverse the values if:
            #   we're moving the curve to the left and the start socket is on the right; or
            #   we're moving to the right and the start socket is on the left
            start_socket_position = self.edge.start_socket.position
            if (s0 > d0 and start_socket_position in (Position.TOP_RIGHT, Position.BOTTOM_RIGHT)) \
                    or (s0 < d0 and start_socket_position in (Position.BOTTOM_LEFT, Position.TOP_LEFT)):
                # reverse the x values
                control_source[0], control_dest[0] = -distance, distance

                # set the y values
                s1 = self.pos_source[1]
                d1 = self.pos_destination[1]
                # avoid div by 0
                div = math.fabs((d1 - s1) if (d1 - s1) != 0 else 0.00001)
                control_source[1] = (d1 - s1) / div * 100
                control_dest[1] = (s1 - d1) / div * 100
        else:
            self.logger.debug("Edge {} {} has no sockets!".format(type(self), self.edge))

        return control_source, control_dest
