#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# UI_SAVE_AS_CONTROLLER #
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
from interaction_manager.view.ui_saveas_dialog import Ui_SaveAsDialog


class UISaveAsController(QtWidgets.QDialog):

    def __init__(self, parent=None, serialized_data=None):
        super(UISaveAsController, self).__init__(parent)

        self.logger = logging.getLogger("SaveAsController")
        self.serialized_data = serialized_data

        # init UI elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_SaveAsDialog()
        self.ui.setupUi(self)
        # current directory
        self.ui.folderNameLineEdit.setText("{}/logs".format(os.getcwd()))

        # file name
        self.ui.fileNameLineEdit.setText("InteractionBlocks_{}".format(
            time.strftime("%d-%m-%y_%H-%M-%S", time.localtime())))

        # button listeners
        self.ui.selectFolderToolButton.clicked.connect(self.select_folder)

    def select_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a folder",
            os.getcwd(),  # expanduser("~"),
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        self.ui.folderNameLineEdit.setText(folder_name)

    def get_full_path(self):
        filename = self.ui.fileNameLineEdit.text()
        folder_name = self.ui.folderNameLineEdit.text()

        return "{}/{}".format(folder_name, filename)

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
