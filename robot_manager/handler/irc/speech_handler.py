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
        self.block_completed_observers = Observable()

        self.speech_certainty = 0.4
        self.voice_pitch = 100
        self.voice_speed = 85

        # add a listener to the keyword stream
        self.session.subscribe(self.on_keyword, "rom.optional.keyword.stream")
        self.current_keywords = []
        self.is_listening = False
        self.start_time = time.time()

    def reset(self):
        pass

    # KEYWORDS
    # ========
    @inlineCallbacks
    def on_keyword(self, frame):
        if (not self.is_listening) and (frame is None or len(frame) == 0):
            self.logger.info("No frames needed!")
            yield
        else:
            try:
                certainty = frame["data"]["body"]["certainty"]

                if certainty >= self.speech_certainty:
                    keyword = frame["data"]["body"]["text"]

                    if keyword in self.current_keywords:
                        self.logger.info("Detected keyword is in the list: {}".format(frame["data"]))
                        self.is_listening = False
                        self.clear_keywords()

                        yield self.keyword_stream(start=False)

                        self.keyword_observers.notify_all(keyword)
                        yield True
                    else:
                        self.logger.info("Keyword received '{}' is not in the list {}".format(
                            keyword, self.current_keywords))
                        yield False
                else:
                    self.logger.info("OnKeyword received with low certainty: {}".format(frame))
                    yield False
            except Exception as e:
                self.logger.error("Error while getting the received answer! | {}".format(e))
                yield False

    @inlineCallbacks
    def add_keywords(self, keywords=None):
        # add keywords to listen to
        if keywords is None:
            yield False
        else:
            yield self.session.call("rom.optional.keyword.add", keywords=keywords)  # keywords = array of strings

    @inlineCallbacks
    def remove_keywords(self, keywords=None):
        if keywords is None:
            yield False
        else:
            yield self.session.call("rom.optional.keyword.remove", keywords=keywords)

    @inlineCallbacks
    def clear_keywords(self):
        self.current_keywords = []
        yield self.session.call("rom.optional.keyword.clear")

    @inlineCallbacks
    def keyword_stream(self, start=False):
        self.logger.info("{} keyword stream.".format("Starting" if start else "Closing"))
        self.is_listening = start
        # start/close the keyword stream
        yield self.session.call("rom.optional.keyword.stream" if start else "rom.optional.keyword.close")

    @inlineCallbacks
    def reset_keyword_stream(self):
        self.clear_keywords()
        yield self.keyword_stream(start=False)

    # BLOCKS
    # =======
    @inlineCallbacks
    def on_block_completed(self, result=None):
        self.logger.info("BlockCompleted callback - notifying observers")
        self.block_completed_observers.notify_all(True)
        yield True

    @inlineCallbacks
    def on_start_listening(self, results):
        yield self.add_keywords(keywords=self.current_keywords)
        yield self.keyword_stream(start=True)

    # ======
    # SPEECH
    # ======
    @inlineCallbacks
    def say(self, message="Hi"):
        text = "\\vct={}\\\\rspd={}\\{}".format(int(self.voice_pitch), int(self.voice_speed), message)
        yield self.session.call("rom.optional.tts.say", text=text)

    @inlineCallbacks
    def animated_say(self, message="", animation_name=None):
        yield self.session.call("rom.optional.tts.animate",
                                text="\\vct={}\\\\rspd={}\\{}".format(int(self.voice_pitch), int(self.voice_speed),
                                                                      message))

    @inlineCallbacks
    def set_volume(self, level=50.0):
        vol = int(level) if level > 1 else int(level * 100)
        self.logger.info("Setting volume to: {}".format(vol))
        yield self.session.call("rom.actuator.audio.volume", volume=vol)

    @inlineCallbacks
    def set_language(self, name="en"):
        # switch to English
        yield self.session.call(u'rom.optional.tts.language', lang="en")
        yield self.session.call("rie.dialogue.config.language", lang="{}".format(name))

    # MEMORY
    def insert(self, data_dict=None):
        if data_dict is None:
            return
        try:
            self.session.call("rom.optional.tts.insert_data", data_dict=data_dict)
        except Exception as e:
            self.logger.error("Error while inserting '{}' into memory: {}".format(data_dict, e))

    @property
    def speech_certainty(self):
        return self.__speech_certainty

    @speech_certainty.setter
    def speech_certainty(self, val):
        val = abs(float(val))
        self.__speech_certainty = val if (0 <= val <= 1) else (val / 100.0)

    # =======
    # HELPERS
    # =======

    def is_valid_string(self, value):
        """
        @return False if value is None or is equal to empty string; and True otherwise.
        """
        return False if (value is None or value.strip() == "") else True

    @inlineCallbacks
    def print_data(self, result):
        yield self.logger.info('Result received: {}'.format(result))
