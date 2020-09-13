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
from interaction_manager.dataservice.mongo_dao import MongoDAO
from interaction_manager.utils import config_helper


class DatabaseController(object):
    def __init__(self):
        self.mongo_dao = None
        self.db_props = config_helper.get_db_mongo_settings()

    def _check_dao(self):
        if self.mongo_dao is None:
            self.mongo_dao = MongoDAO()

    # --------- #
    # MONGO DB
    # --------- #
    def connect(self):
        self._check_dao()
        message, error = (None,) * 2

        success = self.mongo_dao.connect()
        if success is True:
            db_controller = UIDBController(db_list=self.mongo_dao.get_all_databases(self.db_props["blocks_keyname"]))

            if db_controller.exec_():
                db_name = str(db_controller.ui.dbNamesComboBox.currentText())
                self.mongo_dao.set_database(db_name)
                message = "Successfully connected to MongoDB and opened '{}' database.".format(db_name)
        else:
            error = "Error while connecting to MongoDB. \n{}".format(success)

        return message, error

    def disconnect(self):
        message, error = (None,) * 2

        if self.mongo_dao is not None:
            success = self.mongo_dao.disconnect()
            if success is True:
                message = "Successfully disconnected from MongoDB"
            else:
                error = "Error while disconnecting from MongoDB."

            self.mongo_dao = None
        else:
            error = "Database was already disconnected!"

        return message, error

    def set_database(self, db_name):
        self._check_dao()

        db_name = self.db_props["blocks_dbname"] if db_name is None else db_name
        success = self.mongo_dao.set_database(db_name=db_name)

        return success

    def insert_dialogue_design(self, dialogue_design):
        self._check_dao()

        return self.mongo_dao.insert_interaction_design(design=dialogue_design)
