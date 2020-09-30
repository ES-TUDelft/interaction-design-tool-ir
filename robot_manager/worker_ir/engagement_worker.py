#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# ENGAGEMENT_WORKER #
# ================= #
# Handler class for controlling HRI engagement
#
# @author ES
# **

import logging
import time

from twisted.internet.defer import inlineCallbacks

from robot_manager.pepper.handler.engagement_handler import EngagementHandler
from robot_manager.worker_ir.es_worker import ESWorker


class EngagementWorker(ESWorker):
    def __init__(self, robot_name=None, robot_realm=None):
        super().__init__(robot_name, robot_realm)

        self.logger = logging.getLogger("EngagementWorker")

        self.connection_handler = None
        self.engagement_handler = None
        self.notification_interval = 2

    """
    Override parent methods
    """
    @inlineCallbacks
    def on_connect(self, session, details=None):
        try:
            self.logger.debug("Received session: {}".format(session))

            if session is None:
                self.engagement_handler = None
            else:
                self.engagement_handler = EngagementHandler(session=session)
                self.engagement_handler.notification_interval = self.notification_interval

                # switch to English
                yield session.call(u'rom.optional.tts.language', lang="en")
                yield session.call("rom.optional.tts.say", text="Engagement worker is ready.")

                # Start listening to DB Stream
                self.setup_db_stream()

                self.logger.info("Connection to the robot is successfully established.")
        except Exception as e:
            yield self.logger.error("Error while setting the robot controller {}: {}".format(session, e))

    def start_listening_to_db_stream(self):
        observers_dict = {
            "connectRobot": self.connect_robot,
            "disconnectRobot": self.disconnect_robot,
            "startEngagement": self.on_start_engagement,
        }

        self.db_controller.start_db_stream(observers_dict=observers_dict,
                                           db_collection=self.db_controller.interaction_collection)

    """
    Class methods
    """
    def on_face_detected(self, interval=None):
        try:
            self.logger.info("Interval received: {}".format(interval))
            if interval > 10.0:  # a new person has arrived
                # start new interaction
                self.db_controller.update_one(self.db_controller.robot_collection,
                                              data_key="startInteraction",
                                              data_dict={"startInteraction": True, "timestamp": time.time()})
            self.on_engaged(True)
        except Exception as e:
            self.logger.error("Error while storing block completed: {}".format(e))

    def on_engaged(self, val=None):
        try:
            self.db_controller.update_one(self.db_controller.robot_collection,
                                          data_key="isEngaged",
                                          data_dict={"isEngaged": False if val is None else val,
                                                     "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while storing isEngaged: {}".format(e))

    def on_start_engagement(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            start = data_dict["startEngagement"]
            if start is True:
                self.logger.info("Engagement is started.")
                self.engagement_handler.face_detected_observers.add_observer(self.on_face_detected)
                self.engagement_handler.face_detection(start=True)
            else:
                self.logger.info("Engagement is disabled")
                self.engagement_handler.face_detected_observers.remove_observer(self.on_face_detected)
                self.engagement_handler.face_detection(start=False)
        except Exception as e:
            self.logger.error("Error while extracting engagement data: {} | {}".format(data_dict, e))

    @property
    def notification_interval(self):
        return self._notification_interval

    @notification_interval.setter
    def notification_interval(self, interval=2):
        self._notification_interval = interval
        if self.engagement_handler:
            self.engagement_handler.notification_interval = interval
