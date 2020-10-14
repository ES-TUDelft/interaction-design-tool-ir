#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============== #
# SPEECH_HANDLER #
# ============== #
# Handler class for controlling the robot's dialog and speech acts
#
# @author ES
# **

import logging
import time

from twisted.internet.defer import inlineCallbacks

from es_common.model.observable import Observable


class SpeechHandler(object):

    def __init__(self, session):

        self.logger = logging.getLogger("Speech Handler")

        self.session = session

        self.keyword_observers = Observable()

        self.speech_certainty = 0.4
        self.voice_pitch = 100
        self.voice_speed = 85

        self.current_keywords = []
        self.is_listening = False
        self.start_time = time.time()

        # add a listener to the keyword stream
        self.session.subscribe(self.on_keyword, "rom.optional.keyword.stream")

    # KEYWORDS
    # ========
    @inlineCallbacks
    def on_keyword(self, frame):
        if (not self.is_listening) and (frame is None or len(frame) == 0):
            self.logger.info("No frames!")
        else:
            try:
                certainty = frame["data"]["body"]["certainty"]

                if certainty >= self.speech_certainty:
                    keyword = frame["data"]["body"]["text"]

                    if keyword in self.current_keywords:
                        self.logger.info("Detected keyword is in the list: {}".format(frame["data"]))

                        self.is_listening = False
                        yield self.clear_keywords()
                        yield self.keyword_stream(start=False)

                        self.keyword_observers.notify_all(keyword)
                    else:
                        self.logger.info("Keyword received '{}' is not in the list {}".format(
                            keyword, self.current_keywords))
                else:
                    self.logger.info("OnKeyword received with low certainty: {}".format(frame))
            except Exception as e:
                self.logger.error("Error while getting the received answer! | {}".format(e))

    def add_keywords(self, keywords=None):
        # add keywords = [array of strings] to listen to
        self.session.call("rom.optional.keyword.add", keywords=[] if keywords is None else keywords)

    def remove_keywords(self, keywords=None):
        self.session.call("rom.optional.keyword.remove", keywords=[] if keywords is None else keywords)

    def clear_keywords(self):
        self.current_keywords = []
        self.session.call("rom.optional.keyword.clear")

    def keyword_stream(self, start=False):
        # start/close the keyword stream
        self.session.call("rom.optional.keyword.stream" if start else "rom.optional.keyword.close")

    # Listener
    # =========

    def on_start_listening(self, results=None):
        self.is_listening = True
        self.add_keywords(keywords=self.current_keywords)
        self.keyword_stream(start=True)

    # ======
    # SPEECH
    # ======
    def say(self, message="Hi"):
        text = "\\vct={}\\\\rspd={}\\{}".format(int(self.voice_pitch), int(self.voice_speed), message)
        return self.session.call("rom.optional.tts.say", text=text)

    def animated_say(self, message="", animation_name=None):
        text = "\\vct={}\\\\rspd={}\\{}".format(int(self.voice_pitch), int(self.voice_speed), message)
        return self.session.call("rom.optional.tts.animate", text=text)

    def set_volume(self, level=50.0):
        vol = int(level) if level > 1 else int(level * 100)
        self.logger.info("Setting volume to: {}".format(vol))
        self.session.call("rom.actuator.audio.volume", volume=vol)

    def set_language(self, name="en"):
        self.session.call("rom.optional.tts.language", lang=u"{}".format(name))
        self.session.call("rie.dialogue.config.language", lang=u"{}".format(name))

    # MEMORY
    # =======
    def insert(self, data_dict=None):
        try:
            self.session.call("rom.optional.tts.insert_data", data_dict={} if data_dict is None else data_dict)
        except Exception as e:
            self.logger.error("Error while inserting '{}' into memory: {}".format(data_dict, e))

    # PROPERTIES
    # ==========
    @property
    def speech_certainty(self):
        return self.__speech_certainty

    @speech_certainty.setter
    def speech_certainty(self, val):
        val = abs(float(val))
        self.__speech_certainty = val if (0 <= val <= 1) else (val / 100.0)

    # HELPER
    # ======
    @inlineCallbacks
    def print_data(self, result):
        yield self.logger.info('Result received: {}'.format(result))
