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

        self.speech_certainty = 0.5

        # add a listener to the keyword stream
        self.session.subscribe(self.on_keyword, "rom.optional.keyword.stream")
        self.current_keywords = []
        self.is_listening = False
        self.start_time = time.time()
        self.speech_event = None

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
                        self.logger.info("Detected keyword is in the list: {} | {}".format(keyword, certainty))
                        self.is_listening = False
                        self.clear_keywords()

                        self.keyword_stream(start=False)

                        self.keyword_observers.notify_all(keyword)
                        yield
                    else:
                        self.logger.info("Keyword received '{}' is not in the list {}".format(
                            keyword, self.current_keywords))
                        yield
                else:
                    self.logger.info("Frame {} | at {}".format(frame, self.get_time_ms()))
                    yield
            except Exception as e:
                self.logger.error("Error while getting the received answer! | {}".format(e))
                yield

    def get_time_ms(self):
        return time.time() * 1000

    def add_keywords(self, keywords=None):
        # add keywords to listen to
        if keywords is None:
            return

        self.session.call("rom.optional.keyword.add", keywords=keywords)  # keywords = array of strings

    def remove_keywords(self, keywords=None):
        if keywords is None:
            return
        self.session.call("rom.optional.keyword.remove", keywords=keywords)

    def clear_keywords(self):
        self.current_keywords = []
        self.session.call("rom.optional.keyword.clear")

    def keyword_stream(self, start=False):
        self.logger.info("{} keyword stream.".format("Starting" if start else "Closing"))
        self.is_listening = start
        # start/close the keyword stream
        self.session.call("rom.optional.keyword.stream" if start else "rom.optional.keyword.close")

    def reset_keyword_stream(self):
        self.clear_keywords()
        self.keyword_stream(start=False)

    # BLOCKS
    # =======
    @inlineCallbacks
    def on_block_completed(self, result=None):
        self.speech_event = None
        self.logger.info("BlockCompleted callback - notifying observers")
        self.block_completed_observers.notify_all(True)
        yield

    @inlineCallbacks
    def on_start_listening(self, results):
        self.speech_event = None
        self.add_keywords(keywords=self.current_keywords)
        yield self.keyword_stream(start=True)

    # ======
    # SPEECH
    # ======
    def say(self, message="Hi"):
        self.logger.info("Message to say: {}".format(message))
        self.session.call("rom.optional.tts.say", text="{}".format(message))

    def animated_say(self, message="", animation_name=None):
        self.logger.info("Message to animate: {}".format(message))
        return self.session.call("rom.optional.tts.animate", text="{}".format(message))

    def customized_say(self, interaction_block=None):
        if interaction_block is None:
            self.logger.info("No block is received!")
            return False

        self.logger.info("Block's execution is in progress...")

        # say the message
        message = interaction_block.message

        if message is None or message == "":
            self.on_block_completed(True)
        else:
            # update the block's message, if any
            if "{answer}" in message and interaction_block.execution_result:
                message = message.format(answer=interaction_block.execution_result.lower())

            self.logger.info("Message to say: {}".format(message))
            self.speech_event = self.session.call("rom.optional.tts.animate", text="{}".format(message))
            self.logger.info("Called animate...")
            # check if answers are needed
            # TODO: switch to another check
            if interaction_block.topic_tag.topic == "":
                time.sleep(1)  # to keep the API happy :)
                # self.block_completed_observers.notify_all(True)
                self.speech_event.addCallback(self.on_block_completed)
            else:
                keywords = interaction_block.topic_tag.get_combined_answers()
                self.current_keywords = keywords
                self.logger.info("Keywords: {}".format(keywords))

                self.speech_event.addCallback(self.on_start_listening)

    def set_volume(self, level=50.0):
        vol = int(level) if level > 1 else int(level * 100)
        self.session.call("rom.actuator.audio.volume", volume=vol)
        self.logger.info("Volume set to: {}".format(vol))

    def set_language(self, name="en"):
        # switch to English
        self.session.call(u'rom.optional.tts.language', lang="en")
        self.session.call("rie.dialogue.config.language", lang="{}".format(name))

    # Dialog
    def goto_tag(self, tag_name="loadAndFillPageTag", topic="general"):
        self.session.call("rom.optional.tts.goto", tag=tag_name, topic=topic)

    # MEMORY
    def insert(self, data_dict=None):
        if data_dict is None:
            return
        try:
            self.session.call("rom.optional.tts.insert_data", data_dict=data_dict)
        except Exception as e:
            self.logger.error("Error while inserting '{}' into memory: {}".format(data_dict, e))

    # MEMORY
    def get_data(self, name=None):
        if name is None:
            return
        try:
            self.session.call("rom.optional.tts.get_data", name=name)
        except Exception as e:
            self.logger.error("Error while getting data '{}' from memory: {}".format(name, e))

    def log(self, value):
        self.logger.info("Pepper heard: {}".format(value))

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

    def raise_event(self, event_name, event_value):
        self.logger.info("Raised event '{}' to load '{}'".format(event_name, event_value))
        # self.memory.raiseEvent(event_name, event_value)

    @inlineCallbacks
    def print_data(self, result):
        yield self.logger.info('Result received: {}'.format(result))
