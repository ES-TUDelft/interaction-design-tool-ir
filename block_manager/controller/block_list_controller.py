#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# BLOCK_LIST_WIDGET #
# ================= #
# Class for controlling the drag-list of block.
#
# @author ES
# **

import logging

from es_common.utils.qt import QSize, Qt, QByteArray, QDataStream, QIODevice, QMimeData, QPoint
from es_common.utils.qt import QPixmap, QDrag, QIcon
from es_common.utils.qt import QListWidget, QAbstractItemView, QListWidgetItem

from block_manager.utils import config_helper as bconfig_helper


class BlockListWidget(QListWidget):
    def __init__(self, parent=None):
        super(BlockListWidget, self).__init__(parent)

        self.logger = logging.getLogger("BlockListWidget")

        self.icon_dim = bconfig_helper.get_block_size_settings()["list_icon_dim"]
        self._init_ui()

    def _init_ui(self):
        self.setIconSize(QSize(*self.icon_dim))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.add_block_items()

    def add_block_items(self):
        return NotImplementedError

    def get_item_icon(self, item_text):
        return NotImplementedError

    def add_block_item(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(icon if icon is not None else "||")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(*self.icon_dim))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)

    def startDrag(self, *args, **kvargs):
        item = self.currentItem()
        try:
            op_code = item.data(Qt.UserRole + 1)
            self.logger.debug("Dragging item {} | {} | {}".format(op_code, item.text(), item))

            # get the item icon
            item_pixmap = QPixmap(self.get_item_icon(item.text()))
            item_pixmap = item_pixmap.scaled(64, 64, Qt.KeepAspectRatio)

            item_data = QByteArray()
            data_stream = QDataStream(item_data, QIODevice.WriteOnly)
            data_stream << item_pixmap

            try:
                data_stream.writeInt(op_code)
            except Exception as e:
                self.logger.warning("'writeInt' does not exist in QDataStream, using writeInt64 instead. | {}".format(e))
                data_stream.writeInt64(op_code)

            data_stream.writeQString(item.text())

            mime_data = QMimeData()
            mime_data.setData(bconfig_helper.get_block_mimetype(), item_data)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QPoint(item_pixmap.width() / 2, item_pixmap.height() / 2))  # set in middle
            drag.setPixmap(item_pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            self.logger.error("Error while dragging item {} | {}".format(item, e))
        # super(BlockListWidget, self).startDrag(*args, **kvargs)
