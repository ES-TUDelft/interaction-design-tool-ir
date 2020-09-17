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
        self.delay_between_blocks = 1  # in seconds

        # add a listener to the keyword stream
        self.session.subscribe(self.on_keyword, "rom.optional.keyword.stream")
        self.current_keywords = []
        self.is_listening = False

    # KEYWORDS
    # ========
    @inlineCallbacks
    def on_keyword(self, frame):
        if (not self.is_listening) and (frame is None or len(frame) == 0):
            yield self.logger.info("No frames needed!")
        else:
            try:
                certainty = frame["data"]["body"]["certainty"]

                if certainty >= self.speech_certainty:
                    self.is_listening = False
                    self.clear_keywords()

                    self.keyword_stream(start=False)

                    keyword = frame["data"]["body"]["text"]
                    self.logger.info("Detected keyword is: {} | {}".format(keyword, certainty))

                    yield self.keyword_observers.notify_all(keyword)
                else:
                    yield self.logger.info("{} | at {}".format(frame, self.get_time_ms()))
            except Exception as e:
                yield self.logger.error("Error while getting the received answer! | {}".format(e))

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
    def on_block_completed(self, result):
        self.logger.info("Result received: {}".format(result))
        yield self.block_completed_observers.notify_all(True)

    @inlineCallbacks
    def on_start_listening(self, results):
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
            return False

        # update the tablet page
        self._set_page_fields(interaction_block.tablet_page)

        # say the message
        message = interaction_block.message
        # update the block's message, if any
        if "{answer}" in message and interaction_block.execution_result:
            message = message.format(answer=interaction_block.execution_result.lower())
        speech_event = self.animated_say(message=message)

        # check if answers are needed
        # TODO: switch to another check
        if interaction_block.topic_tag.topic == "":
            time.sleep(self.delay_between_blocks)  # to keep the API happy :)
            self.logger.info("Finished executing the block.")
            speech_event.addCallback(self.on_block_completed)
        else:
            self.clear_keywords()
            keywords = interaction_block.topic_tag.get_combined_answers()
            self.current_keywords = keywords
            self.logger.info("Keywords: {}".format(keywords))

            speech_event.addCallback(self.on_start_listening)

    def set_volume(self, level=50.0):
        vol = int(level) if level > 1 else int(level * 100)
        self.session.call("rom.actuator.audio.volume", volume=vol)
        self.logger.info("Volume set to: {}".format(vol))

    def set_language(self, name="en"):
        # switch to English
        self.session.call(u'rom.optional.tts.language', lang="en")
        self.session.call("rie.dialogue.config.language", lang="{}".format(name))

    def log(self, value):
        self.logger.info("Pepper heard: {}".format(value))

    @property
    def speech_certainty(self):
        return self.__speech_certainty

    @speech_certainty.setter
    def speech_certainty(self, val):
        val = abs(float(val))
        self.__speech_certainty = val if (0 <= val <= 1) else (val / 100.0)

    @property
    def delay_between_blocks(self):
        return self.__delay_between_blocks

    @delay_between_blocks.setter
    def delay_between_blocks(self, val):
        val = abs(int(val))
        self.__delay_between_blocks = val if val >= 1 else 1

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

    def _set_page_fields(self, tablet_page):
        pass

    @inlineCallbacks
    def print_data(self, result):
        yield self.logger.info('Result received: {}'.format(result))
