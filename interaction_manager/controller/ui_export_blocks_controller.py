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
from os.path import expanduser

from es_common.utils.qt import QtGui, QtWidgets

from es_common.utils import data_helper
from interaction_manager.view.ui_exportblocks_dialog import Ui_ExportBlocksDialog


class UIExportBlocksController(QtWidgets.QDialog):

    def __init__(self, parent=None, serialized_data=None):
        super(UIExportBlocksController, self).__init__(parent)

        self.logger = logging.getLogger("ExportController")
        self.serialized_data = serialized_data

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

    def select_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a folder",
            os.getcwd(),  # expanduser("~"),
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        self.ui.folderNameLineEdit.setText(folder_name)

    def check_fields(self, folder_name=None, filename=None):
        if folder_name is None or folder_name == "":
            self.display_message(error="ERROR: Please select a folder to save the file.")
            return False

        if filename is None or filename == "":
            self.display_message(error="ERROR: the file name is empty!")
            return False

        return True

    def export_blocks(self):
        filename = self.ui.fileNameLineEdit.text()
        folder_name = self.ui.folderNameLineEdit.text()

        if self.check_fields(folder_name=folder_name, filename=filename) is False:
            return False

        try:
            data_helper.save_to_file(filename="{}/{}.json".format(folder_name, filename),
                                     serialized_data=self.serialized_data)
            self.display_message(message="Successfully exported the design.")
            return True
        except Exception as e:
            self.logger.error("Error while saving design data to: {} | {}".format(filename, e))
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
