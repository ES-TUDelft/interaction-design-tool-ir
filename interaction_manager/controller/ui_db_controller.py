#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========================= #
# UI_DB_CONTROLLER #
# ========================= #
# Class for controlling the DB editor GUI.
#
# @author ES
# **

import datetime
import logging

from PyQt5 import QtCore, QtWidgets

import es_common.hre_config as pconfig
from interaction_manager.view.ui_db_dialog import Ui_DBDialog


class UIDBController(QtWidgets.QDialog):

    def __init__(self, parent=None, db_list=[]):
        super(UIDBController, self).__init__(parent)

        self.logger = logging.getLogger("UIDBController")

        # init UI elements
        self._init_ui(db_list=db_list)
        # give it control
        self.setModal(True)

    def _init_ui(self, db_list=[]):
        self.ui = Ui_DBDialog()
        self.ui.setupUi(self)

        # AVAILABLE DBs:
        # -----------------
        self.ui.dbNamesComboBox.clear()
        # db_list = self.mongo_dao.get_all_databases(keyname = pconfig.db_keyname)
        if (db_list is None) or (len(db_list) == 0):
            db_list = [self.get_formatted_db_name()]
        self.ui.dbNamesComboBox.addItems(db_list)

        # button listeners
        self.ui.generateNamePushButton.clicked.connect(self.generate_db_name)
        self.ui.setDBPushButton.clicked.connect(lambda: self.set_database(db_name=str(self.ui.dbNameLineEdit.text())))
        self.repaint()

    def generate_db_name(self):
        db_name = self.get_formatted_db_name()
        self.ui.dbNameLineEdit.setText(db_name)
        self.set_database(db_name)
        self.repaint()
        return db_name

    def set_database(self, db_name):
        if db_name is None or db_name == "":
            db_name = self.generate_db_name()
        self._update_db_combo_box(db_name=db_name)
        self.repaint()

    def _update_db_combo_box(self, db_name):
        if db_name is None: return
        all_dbs = [self.ui.dbNamesComboBox.itemText(i) for i in range(self.ui.dbNamesComboBox.count())]
        if not (db_name in all_dbs):
            self.ui.dbNamesComboBox.addItem(db_name)
        self.ui.dbNamesComboBox.setCurrentIndex(self.ui.dbNamesComboBox.findText(db_name, QtCore.Qt.MatchFixedString))

    def get_formatted_db_name(self):
        return 'HRE_DB_{0:%d}{0:%b}{0:%Y}_{0:%Hh%M}'.format(datetime.datetime.now())
