#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============================== #
# UI_ROBOT_CONNECTION_CONTROLLER #
# ============================== #
# Class for controlling the robot connection editor GUI.
#
# @author ES
# **

import logging
import time

from PyQt5 import QtCore, QtWidgets, QtGui

import es_common.hre_config as pconfig
from es_common.enums.robot_name import RobotName
from interaction_manager.view.ui_connection_dialog import Ui_ConnectionDialog
from es_common.utils import ip_helper


class UIRobotConnectionController(QtWidgets.QDialog):

    def __init__(self, interaction_controller, parent=None):
        super(UIRobotConnectionController, self).__init__(parent)

        self.logger = logging.getLogger("UIRobotConnection Controller")

        self.interaction_controller = interaction_controller
        self.robot_realm = None
        self.is_awake = False

        self.success = False

        # init UI elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_ConnectionDialog()
        self.ui.setupUi(self)

        # connect listener
        self.ui.connectPushButton.clicked.connect(self.connect)

        if self.interaction_controller is None:
            self.ui.connectPushButton.setEnabled(False)
            self._display_message(error="Unable to connect to robot! Try again later.")

        self.repaint()

    def connect(self):
        self.success = False
        try:
            self.robot_realm = "{}".format(str(self.ui.robotRealmLineEdit.text()).strip())

            self.logger.info("Robot Realm: {}".format(self.robot_realm))

            self._display_message(message="Connecting...")

            robot_name = RobotName[self.ui.robotNameComboBox.currentText().upper()]

            self.interaction_controller.connect_to_robot(robot_name=robot_name, robot_realm=self.robot_realm)

            self.success = True
            self.ui.connectPushButton.setEnabled(False)
            self._display_message(message="Successfully connected to the robot.")
        except Exception as e:
            self.logger.error("Error while connecting to the robot: {}".format(e))
            self._display_message(error="Error while connecting to the robot: {}".format(e))
            self.success = False

    def _display_message(self, message=None, error=None):
        if message is None:
            self.ui.messageTextEdit.setTextColor(QtGui.QColor('red'))  # red text for errors
            self.ui.messageTextEdit.setText(error)
            self.logger.error(error)
        else:
            self.ui.messageTextEdit.setTextColor(QtGui.QColor('white'))
            self.ui.messageTextEdit.setText(message)
            self.logger.info(message)

        self.repaint()

    # ------------------------------------- #
    # Methods for Getting/Setting UI Values #
    # ------------------------------------- #
    """
    ROBOT REALM
    """

    @property
    def robot_realm(self):
        return self.__robot_realm

    @robot_realm.setter
    def robot_realm(self, value):
        self.__robot_realm = None if (value is None or str(value).strip() == '') else str(value).strip()
