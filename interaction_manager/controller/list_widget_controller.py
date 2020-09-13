#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# LIST_WIDGET #
# =========== #
# Extended classes for QListWidget and QListWidgetItem
#
# @author ES
# **

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from es_common.model.interaction_block import InteractionBlock

GUI_NAME = "DialogGUI"


class HREListWidget(QtWidgets.QListWidget):
    check_drop_table = pyqtSignal(bool)
    no_item_selected = pyqtSignal(bool)

    def __init__(self, parent=None, allow_duplicates=True):
        super(HREListWidget, self).__init__(parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.drag_item = None
        self.drag_row = None
        self.allow_duplicates = allow_duplicates

    def mousePressEvent(self, event):
        model_index = self.indexAt(event.pos())
        if model_index.isValid():
            super(HREListWidget, self).mousePressEvent(event)
        else:
            self.clearSelection()
            self.no_item_selected.emit(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(HREListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            super(HREListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        # if isinstance(event.source(), HREListWidget):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
        else:
            drop_index = self.indexAt(event.pos()).row()
            if event.source() is self:  # move item within list
                self._move_item(drop_index=drop_index, item=event.source().currentItem())
            else:  # add a new item
                self._add_item(drop_index=drop_index, item=event.source().currentItem(), randomize=True)
            event.setDropAction(QtCore.Qt.MoveAction)
            super(HREListWidget, self).dropEvent(event)
        self.clearSelection()
        self.check_drop_table.emit(True)

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        lst_dict = {}
        for i in range(self.count()):
            lst_dict['{}'.format(i)] = self.item(i).dialogue_block.to_dict

        return lst_dict

    def _add_item(self, drop_index=0, item=None, randomize=False):
        if item is None: return

        item_copy = item.clone(randomize=randomize)
        item_copy.show_message = True
        item_copy.update_text()
        # check for duplicates
        for i in range(self.count()):
            if self.item(i).text() == item.text():
                if self.allow_duplicates is False:
                    # duplicate found => exit!
                    return
                else:
                    item_copy.setText("{} - {}".format(item.text(), item.counter))
                    # increase name counter of the original item
                    item.counter = item.counter + 1

        # add new item
        self.addItem(item_copy) if drop_index < 0 else self.insertItem(drop_index, item_copy)
        self.repaint()

    def _move_item(self, drop_index=0, item=None):
        if item is None: return
        # add new item
        self.addItem(item.clone()) if drop_index < 0 else self.insertItem(drop_index, item.clone())
        self.takeItem(self.row(item))
        self.repaint()


class HREListWidgetItem(QtWidgets.QListWidgetItem):

    def __init__(self, parent=None, dialogue_block=None, show_message=False):
        super(HREListWidgetItem, self).__init__(parent)

        self.dialogue_block = InteractionBlock() if dialogue_block is None else dialogue_block
        self.setText(QtCore.QCoreApplication.translate(GUI_NAME, self.dialogue_block.name))
        if show_message is True:
            self.update_text()
        self.counter = 1
        self._set_display_properties()

    def _set_display_properties(self):
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.setFont(font)
        if self.dialogue_block.icon_path is not None:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(self.dialogue_block.icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setIcon(icon)

    def update_text(self):
        txt = "{}:\n'{}'".format(self.dialogue_block.name,
                                 self.dialogue_block.speech_act.message)
        self.setText(txt)
        # self.setText(QtCore.QCoreApplication.translate(GUI_NAME, txt))

    def clone(self, randomize=False):
        item = HREListWidgetItem()
        item.setText(self.text())
        item.dialogue_block = self.dialogue_block.clone(randomize=randomize)
        item.counter = self.counter

        item.setFont(self.font())
        item.setIcon(self.icon())

        return item
