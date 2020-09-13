import os

import pymongo

env_name = "CHANGE_STREAM_ROBOT_DB"
os.environ[env_name] = "mongodb://localhost:27017"


class DBHelper(object):
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ[env_name])
        self.db = self.client["RobotDB"]
        self.robot_collection = self.db.collection["RobotCollection"]

    def insert_session(self, session):
        self.robot_collection.insert_one({"robotSession": session})  # TODO: send as BSON
