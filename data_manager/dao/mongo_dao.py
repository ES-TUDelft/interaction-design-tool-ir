#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========= #
# MONGO_DAO #
# ========= #
# Mongo DB access
#
# @author ES
# **

import datetime
import logging

from pymongo import MongoClient

from interaction_manager.utils import config_helper


class MongoDAO(object):
    def __init__(self, host=None, port=None, db_name=None):
        self.logger = logging.getLogger("MongoDAO")

        self.db_props = config_helper.get_db_mongo_settings()
        self.db_name = self.get_formatted_db_name() if db_name is None else db_name
        self.host = self.db_props['host'] if host is None else host
        self.port = self.db_props['port'] if port is None else port
        self.client = None
        self.database = None
        self.is_connected = False

        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(str('mongodb://{}:{}'.format(self.host, self.port)))  # or MongoClient(host, port)
            self.database = self.client[self.db_name]
            self.is_connected = True
            return True
        except Exception as e:
            self.logger.error("Error while connecting to MongoDB: {}".format(e))
            self.is_connected = False
            return False

    def disconnect(self):
        self.is_connected = False
        if self.client is None:
            return False

        self.client.close()
        return True

    '''
    DATABASES
    '''

    def set_database(self, db_name):
        if self.client is None or db_name is None:
            return False

        self.db_name = db_name
        self.database = self.client[db_name]
        return True

    def get_database(self, db_name=None):
        if self.client is None:
            return None

        return self.client[self.db_name] if db_name is None else self.client[db_name]

    def get_all_databases(self, keyname=None):
        if self.client is None: return None
        db_list = []
        if keyname is None:
            db_list = self.client.database_names()
        else:
            dbs = self.client.database_names()
            for db in dbs:
                if keyname in db:
                    db_list.append(db)
        return db_list

    def delete_database(self, db_name):
        try:
            self.client.drop_database(db_name)
            return True
        except Exception as e:
            return e

    '''
    COLLECTIONS
    '''

    def get_all_collections(self):
        if self.client is None:
            return None

        return self.database.collection_names()

    def get_collection(self, col_name=None):
        if self.client is None or col_name is None:
            return None

        return self.database[col_name]

    def _get_blocks_collection_name(self):
        return self.db_props['blocks_collection']

    '''
    DIALOGUE BLOCKS
    '''

    def insert_interaction_design(self, design_dict=None):
        if not self.is_connected:
            return False

        return self._insert(collection=self.database[self._get_blocks_collection_name()],
                            to_insert=design_dict,
                            one_record=True)

    def get_dialogue_designs(self, limit=0):
        if self.client is None:
            return None

        dialogues = []
        try:
            col = self.database[self._get_blocks_collection_name()]
            results = col.find() if limit <= 0 else col.find().limit(limit)

            if results is None:
                return None
            for d_dict in results:
                dialogues.append(d_dict)
        except Exception as e:
            self.logger.info("Error while getting design dialogues: {}".format(e))
        finally:
            return dialogues

    '''
    HELPER METHODS
    '''

    def get_formatted_db_name(self):
        d = datetime.datetime.now()
        # self.db_name = 'DB_{}-{}-{}_{}-{}-{}'.format(d.year, d.month d., d.day, d.hour, d.minute, d.second)
        return 'HRE_DB_{0:%d}{0:%b}{0:%Y}_{0:%Hh%M}'.format(d)

    def _insert(self, collection, to_insert, one_record=True):
        if collection is None or to_insert is None:
            return False
        success = False
        try:
            collection.insert_one(to_insert) if one_record is True else collection.insert_many(to_insert)
            success = True
        except Exception as e:
            self.logger.error("Error while inserting: {}".format(to_insert))
            self.logger.error(e)
        finally:
            return success
