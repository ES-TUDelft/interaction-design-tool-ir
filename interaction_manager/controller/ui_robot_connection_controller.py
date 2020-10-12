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

from es_common.utils import ip_helper
from es_common.utils.qt import QtWidgets, QtGui, QtCore
from interaction_manager.view.ui_connection_dialog import Ui_ConnectionDialog


class UIRobotConnectionController(QtWidgets.QDialog):

    def __init__(self, interaction_controller, parent=None):
        super(UIRobotConnectionController, self).__init__(parent)

        self.logger = logging.getLogger("UIRobotConnection Controller")

        self.interaction_controller = interaction_controller

        self.robot_realm, self.robot_ip, self.robot_port = (None, ) * 3
        self.is_awake = False

        self.success = False

        # init UI elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_ConnectionDialog()
        self.ui.setupUi(self)

        # Set validator and field for IP address
        # self._set_ip_validator(self.ui.robotIPLineEdit)
        # self._set_ip_field(self.ui.robotIPLineEdit)

        # button listener
        self.ui.wampSessionRadioButton.toggled.connect(lambda: self.on_session_radio_button(enable_wamp=True))
        self.ui.qiSessionRadioButton.toggled.connect(lambda: self.on_session_radio_button(enable_qi=True))
        self.on_session_radio_button(enable_wamp=True)

        # connect listener
        self.ui.connectPushButton.clicked.connect(self.on_connect)

        if self.interaction_controller is None:
            self.ui.connectPushButton.setEnabled(False)
            self._display_message(error="Unable to connect to robot! Try again later.")

        self.repaint()

    def on_session_radio_button(self, enable_wamp=False, enable_qi=False):
        self.ui.wampSessionGroupBox.setEnabled(enable_wamp)
        self.ui.qiSessionGroupBox.setEnabled(enable_qi)

    def on_connect(self):
        self.success = False
        try:
            self.robot_realm = "{}".format(str(self.ui.robotRealmLineEdit.text()).strip())
            self.logger.info("Robot Realm: {}".format(self.robot_realm))

            self.robot_ip = str(self.ui.robotIPLineEdit.text()).strip()
            self.robot_port = str(self.ui.robotPortLineEdit.text()).strip()
            self.logger.info("IP: {} - PORT: {}".format(self.robot_ip, self.robot_port))

            self._display_message(message="Connecting...")

            robot_name = self.ui.robotNameComboBox.currentText()

            self.interaction_controller.connect_to_robot(robot_name=robot_name, robot_realm=self.robot_realm,
                                                         robot_ip=self.robot_ip, robot_port=self.robot_port)

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

    @property
    def robot_realm(self):
        return self.__robot_realm

    @robot_realm.setter
    def robot_realm(self, value):
        self.__robot_realm = None if (value is None or str(value).strip() == '') else str(value).strip()

    @property
    def robot_ip(self):
        return self.__robot_ip

    @robot_ip.setter
    def robot_ip(self, value):
        self.__robot_ip = None if (value is None or str(value).strip() == '') else str(value).strip()

    @property
    def robot_port(self):
        return self.__robot_port

    @robot_port.setter
    def robot_port(self, value):
        self.__robot_port = None if (value is None or str(value).strip() == '') else str(value).strip()

    # -------------- #
    # Helper Methods #
    # -------------- #
    def _set_ip_validator(self, line_edit):
        """
        @param line_edit of type QLineEdit
        """
        _range = '(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])'  # [0, 255]
        reg_ex = QtCore.QRegExp(r'^' + _range + '\\.' + _range + '\\.' + _range + '\\.' + _range + '$')
        ip_validator = QtGui.QRegExpValidator(reg_ex, line_edit)
        line_edit.setValidator(ip_validator)

    def _set_ip_field(self, line_edit):
        """
        @param line_edit of type QLineEdit
        """
        try:
            ip_parts = (ip_helper.get_host_ip()).split('.')
            line_edit.setText('{}.{}.{}.{}'.format(ip_parts[0], ip_parts[1], ip_parts[2], 0))
        except Exception as e:
            self._display_message(error="Error while getting the router IP!\n{}".format(e))
