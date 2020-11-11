#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========================== #
# DATABASE_CONTROLLER #
# =========================== #
#
# @author ES
# **

from interaction_manager.controller.ui_db_controller import UIDBController
from data_manager.dao.mongo_dao import MongoDAO
from interaction_manager.utils import config_helper


class DatabaseController(object):
    def __init__(self):
        self.mongo_dao = None
        self.db_props = config_helper.get_db_mongo_settings()

    def _check_dao(self):
        if self.mongo_dao is None:
            self.mongo_dao = MongoDAO()
        elif not self.mongo_dao.is_connected:
            self.mongo_dao.connect()

    # --------- #
    # MONGO DB
    # --------- #
    def connect(self):
        self._check_dao()
        message, error = (None,) * 2

        # init db controller
        if self.mongo_dao.is_connected is True:
            db_keyname = self.db_props["blocks_keyname"]
            db_controller = UIDBController(db_list=self.mongo_dao.get_all_databases(db_keyname),
                                           db_keyname=db_keyname)

            if db_controller.exec_():
                db_name = str(db_controller.ui.dbNamesComboBox.currentText())
                self.mongo_dao.set_database(db_name)
                message = "Successfully connected to MongoDB and opened '{}' database.".format(db_name)
            else:
                self.mongo_dao = None
                error = "Connection is cancelled."
        else:
            self.mongo_dao = None
            error = "Error while connecting to MongoDB."

        return message, error

    def disconnect(self):
        message, error = (None,) * 2

        if self.mongo_dao is None:
            error = "Database was already disconnected!"
        else:
            self.mongo_dao.disconnect()
            self.mongo_dao = None
            message = "Successfully disconnected from MongoDB"

        return message, error

    def set_database(self, db_name):
        self._check_dao()

        db_name = self.db_props["blocks_dbname"] if db_name is None else db_name
        success = self.mongo_dao.set_database(db_name=db_name)

        return success

    def insert_interaction_design(self, design_dict=None):
        self._check_dao()

        return self.mongo_dao.insert_interaction_design(design_dict=design_dict)
