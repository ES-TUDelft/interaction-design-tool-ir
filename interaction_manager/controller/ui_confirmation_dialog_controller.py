#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================================= #
# UI_CONFIRMATION_DIALOG_CONTROLLER #
# ================================= #
# Class for controlling the confirmation GUI.
#
# @author ES
# **

import logging

from es_common.utils.qt import QtCore, QtWidgets

from interaction_manager.view.ui_confirmation_dialog import Ui_ConfirmationDialog


class UIConfirmationDialogController(QtWidgets.QDialog):

    def __init__(self, parent=None, message=None):
        super(UIConfirmationDialogController, self).__init__(parent=parent)

        self.logger = logging.getLogger("Confirmation Dialog")

        # init UI elements
        self._init_ui()
        if message is not None:
            self.set_message(message=message)
        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_ConfirmationDialog()
        self.ui.setupUi(self)

    def set_message(self, message=""):
        self.ui.confirmationTextEdit.clear()
        self.ui.confirmationTextEdit.setText(message)
        self.ui.confirmationTextEdit.setAlignment(QtCore.Qt.AlignCenter)
