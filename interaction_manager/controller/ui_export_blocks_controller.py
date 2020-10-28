#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# UI_EXPORT_BLOCKS_CONTROLLER #
# =========================== #
# Class for controlling the blocks export editor GUI.
#
# @author ES
# **

import logging
import os
import time

from es_common.utils import data_helper
from es_common.utils.qt import QtGui, QtWidgets
from interaction_manager.view.ui_exportblocks_dialog import Ui_ExportBlocksDialog


class UIExportBlocksController(QtWidgets.QDialog):

    def __init__(self, parent=None, serialized_data=None):
        super(UIExportBlocksController, self).__init__(parent)

        self.logger = logging.getLogger("ExportController")
        self.serialized_data = serialized_data

        self.filename = None
        self.folder_name = None

        # init UI elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_ExportBlocksDialog()
        self.ui.setupUi(self)
        # current directory
        self.ui.folderNameLineEdit.setText("{}/logs".format(os.getcwd()))

        # file name
        self.ui.fileNameLineEdit.setText("InteractionBlocks_{}".format(
            time.strftime("%d-%m-%y_%H-%M-%S", time.localtime())))

        # button listeners
        self.ui.selectFolderToolButton.clicked.connect(self.select_folder)
        self.ui.exportBlocksButton.clicked.connect(self.export_blocks)

        self.ui.buttonBox.clicked.connect(self.on_button_box)

    def select_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a folder",
            os.getcwd(),  # expanduser("~"),
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        self.ui.folderNameLineEdit.setText(folder_name)

    def check_fields(self):
        self.filename = self.ui.fileNameLineEdit.text()
        self.folder_name = self.ui.folderNameLineEdit.text()

        if self.folder_name is None or self.folder_name == "":
            self.display_message(error="ERROR: Please select a folder to save the file.")
            return False

        if self.filename is None or self.filename == "":
            self.display_message(error="ERROR: the file name is empty!")
            return False

        return True

    def on_button_box(self, event):
        self.logger.info("{} | {}".format(event.text(), event))

    def export_blocks(self):
        if not self.check_fields():
            return False

        try:
            data_helper.save_to_file(filename="{}/{}.json".format(self.folder_name, self.filename),
                                     serialized_data=self.serialized_data)
            self.display_message(message="Successfully exported the design.")
            return True
        except Exception as e:
            self.logger.error("Error while saving design data to: {} | {}".format(self.filename, e))
            return False

    def display_message(self, message=None, error=None):
        if message is None:
            self.ui.messageTextEdit.setTextColor(QtGui.QColor('red'))  # red text for errors
            self.ui.messageTextEdit.setText(error)
            self.logger.error(error)
        else:
            self.ui.messageTextEdit.setTextColor(QtGui.QColor('white'))
            self.ui.messageTextEdit.setText(message)
            self.logger.info(message)

        self.repaint()
