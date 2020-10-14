#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================== #
# ENGAGEMENT_HANDLER #
# ================== #
# Handler class for controlling the robot's engagement
#
# @author ES
# **

import logging
import time

from es_common.model.observable import Observable


class EngagementHandler(object):

    def __init__(self, session):
        self.logger = logging.getLogger("EngagementHandler")

        self.session = session

        self.memory = self.session.service("ALMemory")
        self.face_service = self.session.service("ALFaceDetection")
        self.tracker = self.session.service("ALTracker")

        self.min_face_size = 0.2  # rads
        self.tracker_face_size = 0.1
        self.last_time_detected = 0  # log the time
        self.notification_interval = 2  # seconds

        # observers
        self.face_detected_observers = Observable()
        self.face_subscriber = None

        # subscribe to face events
        self.face_events(subscribe=True)

    # SUBSCRIBE
    # =========
    def face_events(self, subscribe=True):
        if subscribe:
            self.face_subscriber = self.memory.subscriber("FaceDetected")
            self.face_subscriber.signal.connect(self.on_face_detected)
            self.face_service.subscribe("ESEngagementHandler")
        else:
            self.face_subscriber = None
            self.face_service.unsubscribe("ESEngagementHandler")

    def on_face_detected(self, value):
        # self.logger.info("Face detected: {}".format(value))
        try:
            if value is None or value == []:
                time.sleep(1)
            else:
                faces_info = value[1]

                # skip empty frames
                if faces_info and len(faces_info) > 0:
                    faces_info.pop()  # rec info
                    face_size = 0.0
                    for f_info in faces_info:
                        tmp_size = max(f_info[0][3], f_info[0][4])
                        face_size = max(face_size, tmp_size)

                    if face_size >= self.min_face_size:
                        # > x seconds: notify observers
                        detection_interval = time.time() - self.last_time_detected
                        if detection_interval >= self.notification_interval:
                            self.logger.info("Detected a face: {} | after {}s".format(face_size, detection_interval))
                            self.last_time_detected = time.time()
                            self.face_detected_observers.notify_all(detection_interval)
                else:
                    time.sleep(1)
        except Exception as e:
            self.logger.error("Error while receiving the detected face: {}".format(e))

    def face_detection(self, start=False):
        # start/close the face stream
        if start:
            self.face_service.subscribe("ESEngagementHandler")
        else:
            self.face_service.unsubscribe("ESEngagementHandler")

    def face_tracker(self, start=False):
        target_name = "Face"
        if start is True:
            self.tracker.registerTarget(target_name, self.tracker_face_size)
            self.tracker.track(target_name)
        else:
            self.tracker.stopTracker()
            self.tracker.unregisterAllTargets()
