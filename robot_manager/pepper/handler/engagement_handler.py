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

from twisted.internet.defer import inlineCallbacks

from es_common.model.observable import Observable


class EngagementHandler(object):

    def __init__(self, session):
        self.logger = logging.getLogger("EngagementHandler")

        self.session = session
        # yield self.session.call("rie.dialogue.say", text="Face detection is on")

        self.face_detected_observers = Observable()

        self.face_certainty = 0.5
        # subscribe to face events
        self.session.subscribe(self.on_face_detected, "rom.optional.face.stream")

    @inlineCallbacks
    def on_face_detected(self, frame):
        try:
            if frame is None or len(frame) == 0:
                yield
            else:
                detected_face = frame["data"]["body"]
                if detected_face is not None and len(detected_face) > 0:
                    # certainty = frame["data"]["body"]["certainty"]
                    # self.logger.info("Certainty = {}".format(certainty))
                    # if certainty >= self.face_certainty:

                    self.logger.info("Detected a face: {}".format(frame["data"]))
                    yield  # self.face_detected_observers.notify_all(frame["data"])
                else:
                    yield  # self.logger.info(frame["data"])
        except Exception as e:
            yield self.logger.error("Error while receiving the detected face: {}".format(e))

        # yield self.session.call("rom.optional.tts.language", lang="en")
        # yield self.session.call("rom.optional.tts.animate", text="I see you")

    def face_detection(self, start=False):
        self.session.call("rom.optional.face.close")
        # start/close the face stream
        # self.session.call("rom.optional.face.stream" if start else "rom.optional.face.close")

    @property
    def face_certainty(self):
        return self.__face_certainty

    @face_certainty.setter
    def face_certainty(self, val):
        val = abs(float(val))
        self.__face_certainty = val if (0 <= val <= 1) else (val / 100.0)
