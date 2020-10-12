#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# IRC_WORKER #
# ================= #
# Abstract worker class
#
# @author ES
# **

import logging
import time

from autobahn.twisted import sleep
from twisted.internet.defer import inlineCallbacks

from data_manager.controller.db_stream_controller import DBStreamController
from es_common.enums.robot_enums import RobotName
from robot_manager.handler.irc.connection_handler import ConnectionHandler


class IRCWorker(object):
    def __init__(self):
        self.logger = logging.getLogger("IRCWorker")

        self.robot_name, self.robot_realm = (None, ) * 2
        self.db_stream_controller = DBStreamController()
        self.connection_handler = None

        self.is_interacting = False

        self.is_connected = False

    def connect_robot(self, data_dict=None):
        try:
            if data_dict is None:
                data_dict = self.db_stream_controller.find_one(coll=self.db_stream_controller.interaction_collection,
                                                               data_key="connectRobot")

            self.robot_name = data_dict["connectRobot"]["robotName"]
            self.robot_realm = data_dict["connectRobot"]["robotRealm"]

            self.connection_handler = ConnectionHandler()
            self.connection_handler.session_observers.add_observer(self.on_connect)

            self.logger.info("Connecting...")
            self.connection_handler.start_rie_session(robot_name=self.robot_name,
                                                      robot_realm=self.robot_realm)

            self.logger.info("Successfully connected to the robot")
        except Exception as e:
            self.logger.error("Error while connecting to the robot: {}".format(e))

    @inlineCallbacks
    def on_connect(self, session, details=None):
        """
        TO be implemented by child classes
        """
        try:
            self.logger.debug("Received session: {}".format(session))

            if session is None:
                yield sleep(1)
            else:
                yield session.call("rom.optional.tts.say", text="Received the session in abstract worker.")
                self.is_connected = True

                # Start listening to DB Stream
                self.setup_db_stream()

                self.logger.info("Connection to the robot is successfully established.")
        except Exception as e:
            yield self.logger.error("Error while setting the robot controller {}: {}".format(session, e))

    def disconnect_robot(self, data_dict=None):
        if self.connection_handler:
            self.logger.info("Disconnecting from robot...")
            self.connection_handler.stop_session()
            time.sleep(2)
            self.connection_handler = None
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
