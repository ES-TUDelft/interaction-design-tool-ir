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

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

from es_common.model.observable import Observable


class EngagementHandler(object):

    def __init__(self, session):
        self.logger = logging.getLogger("EngagementHandler")

        self.session = session

        self.min_face_size = 0.2  # rads
        self.last_time_detected = 0  # log the time
        self.notification_interval = 2  # seconds

        # observers
        self.face_detected_observers = Observable()

        # subscribe to face events
        self.session.subscribe(self.on_face_detected, "rom.optional.face.stream")

    @inlineCallbacks
    def on_face_detected(self, frame):
        try:
            if frame is None or len(frame) == 0:
                yield sleep(1)
            else:
                detected_face = frame["data"]["body"]
                # skip empty frames
                if detected_face and len(detected_face) > 0:
                    # check face size
                    face_size = frame["data"]["body"][0][2]
                    if face_size >= self.min_face_size:
                        # > x seconds: notify observers
                        detection_interval = time.time() - self.last_time_detected
                        if detection_interval >= self.notification_interval:
                            self.logger.info("Detected a face: {} | after {}s".format(frame["data"], detection_interval))
                            self.last_time_detected = time.time()
                            self.face_detected_observers.notify_all(detection_interval)
                    yield sleep(1)
                else:
                    yield sleep(1)
        except Exception as e:
            self.logger.error("Error while receiving the detected face: {}".format(e))
            yield sleep(1)

    def face_detection(self, start=False):
        # start/close the face stream
        self.session.call("rom.optional.face.stream" if start else "rom.optional.face.close")

    def face_tracker(self, start=False):
        self.session.call("rom.optional.face.face_tracker", start=start)
