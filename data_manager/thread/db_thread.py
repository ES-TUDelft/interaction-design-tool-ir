#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================= #
# DB_CHANGE_STREAM_THREAD #
# ======================= #
# Threads for listening to db changes
#
# @author ES
# **

import logging
import time
from threading import Thread

from pymongo.errors import PyMongoError

from es_common.model.observable import Observable
from es_common.utils.qt import QThread


# ###
# DBChangeStreamQThread: inherits QThread
#       This requires a Qt application to run
# ###
class DBChangeStreamQThread(QThread):
    def __init__(self):
        QThread.__init__(self)

        self.logger = logging.getLogger("DBChangeStreamQThread")
        self.change_stream = None
        self.is_listening = False
        self._db_change_observers_dict = {}

    def __del__(self):
        try:
            self.wait()
        except RuntimeError as e:
            self.logger.warning("{}".format(e))

    def stop_running(self):
        self.is_listening = False

    def start_listening(self, db_collection):
        if not self.isRunning():
            self.is_listening = True
            self.change_stream = db_collection.watch(full_document='updateLookup')
            self.logger.info("Started listening to db changes in robot collection.")
            self.start()

    def reset(self):
        self._db_change_observers_dict = {}
        self.is_listening = False
        self.change_stream = None

    def add_data_observers(self, observers_dict):
        for data_key in observers_dict.keys():
            self.add_data_observer(data_key=data_key, observer=observers_dict[data_key])

    def add_data_observer(self, data_key, observer):
        try:
            if data_key not in self._db_change_observers_dict.keys():
                self._db_change_observers_dict[data_key] = Observable()

            self._db_change_observers_dict[data_key].add_observer(observer)
        except Exception as e:
            self.logger.error("Error while adding observer '{}' to '{}' | {}".format(observer, data_key, e))

    def notify_observers(self, data):
        if data is None or len(data) == 0:
            return

        for key in data.keys():
            if key == "_id" or key == "timestamp":
                continue
            try:
                # self.logger.info("The key inserted in db is: {}".format(key))
                if key in self._db_change_observers_dict.keys():
                    self.logger.info("Notifying observers of: {}".format(key))
                    self._db_change_observers_dict[key].notify_all(data)
            except Exception as e:
                self.logger.error("Error while notifying observers of '{}': {} | {}".format(key, data, e))

    def run(self):
        try:
            for change in self.change_stream:
                if not self.is_listening:
                    break
                try:
                    # self.logger.info(change)
                    data = change['fullDocument']
                    # self.logger.info(data)
                    self.notify_observers(data)
                except Exception as e:
                    self.logger.error("Error while getting change: {} | {}".format(change, e))
                    continue

            self.logger.info("Sleeping...")
            time.sleep(1)
        except PyMongoError as e:
            self.logger.error("DB ChangeStream encountered an error: {} | {}".format(self.change_stream, e))
        except Exception as e:
            self.logger.error("Error while getting the data stream: {} | {}".format(self.change_stream, e))

        self.logger.info("Stopped listening to DB changes...")


# ##
# DBChangeStreamThread: inherits Thread
###
class DBChangeStreamThread(Thread):
    is_listening = False

    def __init__(self):
        Thread.__init__(self)

        self.logger = logging.getLogger("DBChangeStreamThread")

        self.change_stream = None
        self._db_change_observers_dict = {}

    def stop_running(self):
        self.is_listening = False

    def start_listening(self, db_collection):
        if not self.is_alive():
            self.is_listening = True
            self.change_stream = db_collection.watch(full_document='updateLookup')
            self.logger.info("Started listening to db changes in robot collection.")
            self.start()

    def reset(self):
        self._db_change_observers_dict = {}
        self.is_listening = False
        self.change_stream = None

    def add_data_observers(self, observers_dict):
        for data_key in observers_dict.keys():
            self.add_data_observer(data_key=data_key, observer=observers_dict[data_key])

    def add_data_observer(self, data_key, observer):
        try:
            if data_key not in self._db_change_observers_dict.keys():
                self._db_change_observers_dict[data_key] = Observable()

            self._db_change_observers_dict[data_key].add_observer(observer)
        except Exception as e:
            self.logger.error("Error while adding observer '{}' to '{}' | {}".format(observer, data_key, e))

    def notify_observers(self, data):
        if data is None or len(data) == 0:
            return

        for key in data.keys():
            if key == "_id" or key == "timestamp":
                continue
            try:
                # self.logger.info("The key inserted in db is: {}".format(key))
                if key in self._db_change_observers_dict.keys():
                    self.logger.info("Notifying observers of: {}".format(key))
                    self._db_change_observers_dict[key].notify_all(data)
            except Exception as e:
                self.logger.error("Error while notifying observers of '{}': {} | {}".format(key, data, e))

    def run(self):
        try:
            for change in self.change_stream:
                if not self.is_listening:
                    break
                try:
                    # self.logger.info(change)
                    data = change['fullDocument']
                    # self.logger.info(data)
                    self.notify_observers(data)
                except Exception as e:
                    self.logger.error("Error while getting change: {} | {}".format(change, e))
                    continue

            self.logger.info("Sleeping...")
            time.sleep(1)
        except PyMongoError as e:
            self.logger.error("DB ChangeStream encountered an error: {} | {}".format(self.change_stream, e))
        except Exception as e:
            self.logger.error("Error while getting the data stream: {} | {}".format(self.change_stream, e))

        self.logger.info("Stopped listening to DB changes...")
