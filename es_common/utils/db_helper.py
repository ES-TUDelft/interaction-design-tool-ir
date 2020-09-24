import logging
import os

import pymongo

env_name = "CHANGE_STREAM_ROBOT_DB"
os.environ[env_name] = "mongodb://localhost:27017"


class DBHelper(object):
    def __init__(self):
        self.logger = logging.getLogger("DBHelper")
        self.client = pymongo.MongoClient(os.environ[env_name])
        self.db = self.client["RobotDB"]
        self.robot_collection = self.db.collection["RobotCollection"]
        self.interaction_collection = self.db.collection["InteractionCollection"]

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
