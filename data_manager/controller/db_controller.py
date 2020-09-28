import logging
import os
import time

import pymongo

from thread_manager.db_thread import DBChangeStreamThread, DBChangeStreamQThread

env_name = "CHANGE_STREAM_ROBOT_DB"
os.environ[env_name] = "mongodb://localhost:27017"


class DBController(object):
    def __init__(self):
        self.logger = logging.getLogger("DBController")
        self.client = pymongo.MongoClient(os.environ[env_name])
        self.db = self.client["RobotDB"]
        self.robot_collection = self.db.collection["RobotCollection"]
        self.interaction_collection = self.db.collection["InteractionCollection"]
        self.db_change_thread = None

    def start_db_stream(self, observers_dict, db_collection, target_thread=None):
        """
        Observers_dict:
            key = name of the data being observed
            value =  observer, i.e., callback to notify
        Target_Thread: use "qt" to create a QThread; and None otherwise
        """
        self.stop_db_stream()  # just in case it was already running

        if target_thread == "qt":
            self.db_change_thread = DBChangeStreamQThread()
        else:
            self.db_change_thread = DBChangeStreamThread()

        self.db_change_thread.add_data_observers(observers_dict=observers_dict)

        self.db_change_thread.start_listening(db_collection)
        self.logger.info("Started listening to DB change stream.")

    def stop_db_stream(self):
        try:
            if self.db_change_thread is not None:
                self.db_change_thread.stop_running()
                self.update_one(self.interaction_collection,
                                data_key="dbChangeStream",
                                data_dict={"dbChangeStream": False, "timestamp": time.time()})
                time.sleep(2)
                # if self.db_change_thread and self.db_change_thread.is_alive():
                #     self.logger.info("DB Thread is still alive!")

                self.logger.info("DB Thread is stopped.")
        except Exception as e:
            self.logger.error("Error while stopping thread: {} | {}".format(self.db_change_thread, e))
        finally:
            self.db_change_thread = None

    def drop(self, coll=None):
        try:
            if coll is None:
                # drop all collections
                self.robot_collection.drop()
                self.interaction_collection.drop()
            else:
                coll.drop()
        except Exception as e:
            self.logger.error("Error while dropping DB collection: {} | {}".format(coll, e))

    def update_one(self, coll, data_key, data_dict):
        if data_dict is None:
            return
        try:
            self.logger.info("Inserting '{}' into db".format(data_key))
            query = {} if data_key is None else {data_key: {"$exists": True}}
            coll.update_one(query, {"$set": data_dict}, upsert=True)
        except Exception as e:
            self.logger.error("Error while inserting '{}' into collection {}: {}".format(data_dict, coll, e))

    def find(self, coll, data_key=None):
        try:
            query = {} if data_key is None else {data_key: {"$exists": True}}
            results = coll.find(query)
            self.logger.info("Results found: {}".format(results))
            return results
        except Exception as e:
            self.logger.error("Error while fetching data '{}' from coll {}: {}".format(data_key, coll, e))
            return None

    def find_one(self, coll, data_key=None):
        try:
            query = {} if data_key is None else {data_key: {"$exists": True}}
            result = coll.find_one(query)
            self.logger.info("Record found: {}".format(result))
            return result
        except Exception as e:
            self.logger.error("Error while fetching data '{}' from coll {}: {}".format(data_key, coll, e))
            return None
