#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# UI_IMPORT_BLOCKS_CONTROLLER #
# =========================== #
# Class for controlling the blocks import editor GUI.
#
# @author ES
# **

import logging

from PyQt5 import QtGui, QtWidgets

from es_common.utils import data_helper
from interaction_manager.view.ui_importblocks_dialog import Ui_ImportBlocksDialog
from interaction_manager.utils import config_helper


class UIImportBlocksController(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(UIImportBlocksController, self).__init__(parent)

        self.logger = logging.getLogger("ImportController")
        self.blocks_data = None

        # init UI elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_ImportBlocksDialog()
        self.ui.setupUi(self)

        # button listeners
        self.ui.selectFileToolButton.clicked.connect(self.select_file)

    def select_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select JSON file", "", "JSON Files (*.json)",
                                                             options=options)

        self.ui.fileNameLineEdit.setText(file_path)
        if file_path is None: return

        self.import_blocks()

    def get_property(self, data, name):
        try:
            p = data[name] if name in data.keys() else None
            return p
        except Exception as e:
            self.logger.error("Error while checking the property '{}' | {}".format(name, e))
            return None

    def import_blocks(self):
        error, message = (None,) * 2
        filename = self.ui.fileNameLineEdit.text()

        if filename is None or filename == "":
            self.display_message(error="ERROR: Please select a file to import.")
            return

        try:
            self.blocks_data = data_helper.load_data_from_file(filename)
            # for b_data in self.blocks_data["blocks"]:
            #     pattern = config_helper.get_patterns()[b_data["title"].lower()]
            #     # bg_color = self.get_property(b_data, "bg_color")
            #     if "bg_color" in pattern.keys():
            #         # self.logger.debug("Setting bg_color for: {}".format(b_data["title"]))
            #         b_data["bg_color"] = pattern["bg_color"]
            #     if "icon" in pattern.keys():
            #         # self.logger.debug("Setting icon for: {}".format(b_data["title"]))
            #         b_data["icon"] = pattern["icon"]

            message = "Data successfully imported."
        except Exception as e:
            error = "{} | {}".format("Error while importing data!" if error is None else error, e)
        finally:
            self.display_message(message=message, error=error)

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
