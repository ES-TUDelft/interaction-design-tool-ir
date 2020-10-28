#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# ENGAGEMENT_WORKER #
# ================= #
# Worker class for controlling HRI engagement
#
# @author ES
# **

import logging
import time

from robot_manager.handler.qi.engagement_handler import EngagementHandler
from robot_manager.worker.qi.qi_worker import QIWorker


class EngagementWorker(QIWorker):
    def __init__(self):
        super(EngagementWorker, self).__init__()

        self.logger = logging.getLogger("EngagementWorker")

        self.connection_handler = None
        self.engagement_handler = None

        self.notification_interval = 1.0  # seconds
        self.interaction_interval = 30.0  # seconds
        self.face_size = 0.2

    """
    Override parent methods
    """

    def connect_robot(self, data_dict=None):
        try:
            super(EngagementWorker, self).connect_robot(data_dict=data_dict)

            # set handlers and listeners
            self.engagement_handler = EngagementHandler(session=self.session)
            self.engagement_handler.notification_interval = self.notification_interval

            # update settings
            self.on_face_size(
                data_dict=self.db_stream_controller.find_one(self.db_stream_controller.interaction_collection,
                                                             "faceSize"))
            self.on_interaction_interval(
                data_dict=self.db_stream_controller.find_one(self.db_stream_controller.interaction_collection,
                                                             "interactionInterval"))

            # start tracker
            self.engagement_handler.face_detection(start=True)
            self.engagement_handler.face_tracker(start=True)

            self.logger.info("Engagement worker is up and running.")
        except Exception as e:
            self.logger.error("Error while starting engagement worker: {}".format(e))

    def start_listening_to_db_stream(self):
        observers_dict = {
            "connectRobot": self.connect_robot,
            "disconnectRobot": self.disconnect_robot,
            "startEngagement": self.on_start_engagement,
            "resumeEngagement": self.on_resume_engagement,
            "faceSize": self.on_face_size,
            "interactionInterval": self.on_interaction_interval
        }
        # Listen to the "interaction_collection"
        self.db_stream_controller.start_db_stream(observers_dict=observers_dict,
                                                  db_collection=self.db_stream_controller.interaction_collection)

    """
    Class methods
    """

    def on_resume_engagement(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.engagement_handler.face_detection(start=True)
        except Exception as e:
            self.logger.error("Error while resuming engagement: {}".format(e))

    def on_start_engagement(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            start = data_dict["startEngagement"]
            if start is True:
                self.logger.info("Engagement is started.")
                self.engagement_handler.face_detected_observers.add_observer(self.on_face_detected)
                self.engagement_handler.face_detection(start=True)
                self.engagement_handler.face_tracker(start=True)
            else:
                self.logger.info("Engagement is disabled")
                self.engagement_handler.face_detected_observers.remove_observer(self.on_face_detected)
                self.engagement_handler.face_detection(start=False)
                self.engagement_handler.face_tracker(start=False)
        except Exception as e:
            self.logger.error("Error while extracting engagement data: {} | {}".format(data_dict, e))

    def on_face_detected(self, face_size=None):
        self.check_for_start_interaction()

        try:
            self.db_stream_controller.update_one(self.db_stream_controller.robot_collection,
                                                 data_key="faceDetected",
                                                 data_dict={"faceDetected": face_size,
                                                            "timestamp": time.time()})
            if face_size >= self.face_size:
                self.db_stream_controller.update_one(self.db_stream_controller.robot_collection,
                                                     data_key="isEngaged",
                                                     data_dict={"isEngaged": True,
                                                                "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while storing isEngaged: {}".format(e))

    def check_for_start_interaction(self):
        try:
            data_dict = self.db_stream_controller.find_one(self.db_stream_controller.interaction_collection,
                                                           "isInteracting")
            elapsed_time = time.time() - data_dict["timestamp"]

            if (data_dict["isInteracting"] is False) and (elapsed_time >= self.interaction_interval):
                self.logger.info("Starting a new interaction after {}s...\n".format(elapsed_time))

                # call for start new interaction
                self.db_stream_controller.update_one(self.db_stream_controller.robot_collection,
                                                     data_key="startInteraction",
                                                     data_dict={"startInteraction": True, "timestamp": time.time()})
                # pause face_detection
                self.engagement_handler.face_detection(start=False)
        except Exception as e:
            self.logger.error("Error while checking isInteracting data: {}".format(e))

    def on_face_size(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.face_size = float(data_dict["faceSize"])
            self.logger.info("Setting minimum face size to: {}".format(self.face_size))
        except Exception as e:
            self.logger.error("Error while extracting face size: {} | {}".format(data_dict, e))

    def on_interaction_interval(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.interaction_interval = float(data_dict["interactionInterval"])
            self.logger.info("Setting interaction interval to: {}".format(self.interaction_interval))
        except Exception as e:
            self.logger.error("Error while extracting interaction interval: {} | {}".format(data_dict, e))

    @property
    def notification_interval(self):
        return self._notification_interval

    @notification_interval.setter
    def notification_interval(self, interval=2):
        self._notification_interval = interval
        if self.engagement_handler:
            self.engagement_handler.notification_interval = interval

    @property
    def interaction_interval(self):
        return self._interaction_interval

    @interaction_interval.setter
    def interaction_interval(self, interval=30.0):
        self._interaction_interval = interval

    @property
    def face_size(self):
        return self._face_size

    @face_size.setter
    def face_size(self, val=0.2):
        self._face_size = val
