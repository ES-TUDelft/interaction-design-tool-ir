#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# QI_WORKER #
# ================= #
# Abstract worker class
#
# @author ES
# **

import logging
import time

from data_manager.controller.db_stream_controller import DBStreamController
from es_common.enums.robot_enums import RobotName
from robot_manager.handler.qi.connection_handler import ConnectionHandler


class QIWorker(object):
    def __init__(self):
        self.logger = logging.getLogger("QIWorker")

        self.robot_name = None
        self.robot_ip = None
        self.robot_port = 9559
        self.app = None
        self.session = None

        self.db_stream_controller = DBStreamController()

        self.is_interacting = False

        self.is_connected = False

    def connect_robot(self, data_dict=None):
        try:
            if not data_dict:  # if None or len == 0
                data_dict = self.db_stream_controller.find_one(coll=self.db_stream_controller.interaction_collection,
                                                               data_key="connectRobot")
            self.robot_name = data_dict["connectRobot"]["robotName"]
            self.robot_ip = data_dict["connectRobot"]["robotIP"]
            self.robot_port = data_dict["connectRobot"]["robotPort"]

            self.logger.info("Connecting...")
            self.app = ConnectionHandler.create_qi_app(name="QIWorker",
                                                       robot_ip=self.robot_ip, robot_port=self.robot_port)
            self.app.start()
            self.session = self.app.session

            self.is_connected = True

            # Start listening to DB Stream
            self.setup_db_stream()

            self.logger.info("Connection to the robot is successfully established.")

            # self.app.run()
        except Exception as e:
            self.logger.error("Error while connecting to the robot: {}".format(e))

    def disconnect_robot(self, data_dict=None):
        self.is_connected = False
        if self.app:
            self.app.stop()
        time.sleep(1)
        self.logger.info("Disconnected from robot.")

    def exit_gracefully(self, data_dict=None):
        try:
            self.disconnect_robot()
            self.db_stream_controller.stop_db_stream()
            self.db_stream_controller.update_one(self.db_stream_controller.interaction_collection,
                                                 data_key="isConnected",
                                                 data_dict={"isConnected": False, "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while exiting: {}".format(e))

    def setup_db_stream(self):
        try:
            self.db_stream_controller.update_one(self.db_stream_controller.robot_collection,
                                                 data_key="isConnected",
                                                 data_dict={"isConnected": True, "timestamp": time.time()})

            self.start_listening_to_db_stream()
            self.logger.info("Finished")
        except Exception as e:
            self.logger.error("Error while setting up db stream: {}".format(e))

    def start_listening_to_db_stream(self):
        """
        To be overridden by child classes
        """
        observers_dict = {
            "connectRobot": self.connect_robot,
            "disconnectRobot": self.disconnect_robot
        }
        # Listen to the "interaction_collection"
        self.db_stream_controller.start_db_stream(observers_dict=observers_dict,
                                                  db_collection=self.db_stream_controller.interaction_collection)

    def has_tablet(self):
        return True if self.robot_name.lower() == RobotName.PEPPER.name.lower() else False

    def run(self):
        self.logger.info("Started running QI Worker")
        try:
            while self.is_connected:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.warning("Interrupted, stopping Qi Worker.")
