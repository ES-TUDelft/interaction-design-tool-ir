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

from es_common.model.observable import Observable


class SpeechHandler(object):

    def __init__(self, session):

        self.logger = logging.getLogger("Speech Handler")

        self.session = session

        self.tts = self.session.service("ALTextToSpeech")
        self.animated_speech = self.session.service("ALAnimatedSpeech")
        self.memory = self.session.service("ALMemory")
        self.speech_recognition = self.session.service("ALSpeechRecognition")
        self.audio = session.service("ALAudioDevice")

        self.keyword_observers = Observable()

        self.speech_certainty = 0.4
        self.voice_pitch = 100
        self.voice_speed = 85

        self.current_keywords = []
        self.is_listening = False
        self.start_time = time.time()

        # add a listener to the keyword stream
        self.keyword_listener = None
        self.keyword_events(subscribe=True)

    # SUBSCRIBE
    # =========
    def keyword_events(self, subscribe=True):
        try:
            if subscribe:
                self.keyword_listener = self.memory.subscriber("WordRecognized")
                self.keyword_listener.signal.connect(self.on_keyword)
            else:
                self.keyword_listener = None
        except Exception as e:
            self.logger.error("Error while subscribing to recognized word event: {}".format(e))

    # KEYWORDS
    # ========
    def on_keyword(self, value=None):
        self.logger.info("OnKeyword: value = {}".format(value))

        if (not self.is_listening) and (value is None or len(value) == 0):
            self.logger.info("No keywords!")
        else:
            try:
                certainty = value[1]

                if certainty >= self.speech_certainty:
                    keyword = value[0]

                    if keyword in self.current_keywords:
                        self.logger.info("Detected keyword is in the list: {}".format(value))

                        self.is_listening = False
                        self.clear_keywords()
                        self.keyword_stream(start=False)

                        self.keyword_observers.notify_all(keyword)
                    else:
                        self.logger.info("Keyword received '{}' is not in the list {}".format(
                            keyword, self.current_keywords))
                else:
                    self.logger.info("OnKeyword received with low certainty: {}".format(value))
            except Exception as e:
                self.logger.error("Error while getting the received answer! | {}".format(e))

    def add_keywords(self, keywords=None):
        # add keywords = [array of strings] to listen to
        if keywords:
            try:
                self.logger.info("Adding keywords: {}".format(keywords))
                self.speech_recognition.pause(True)
                self.speech_recognition.setVocabulary(keywords, False)
                self.speech_recognition.pause(False)
            except Exception as e:
                self.logger.error("Error while adding keywords: {} | {}".format(keywords, e))

    def remove_keywords(self, keywords=None):
        if keywords is None:
            keywords = []
        try:
            self.speech_recognition.pause(True)
            # self.speech_recognition.setVocabulary([k for k in self.current_keywords if k not in keywords], False)
        except Exception as e:
            self.logger.error("Error while removing keywords: {} | {}".format(keywords, e))

    def clear_keywords(self):
        self.current_keywords = []
        # self.remove_keywords()

    def keyword_stream(self, start=False):
        # start/close the speech recognition engine
        self.logger.info("Speech recognition engine {}.".format("is starting" if start else "is stopped"))
        if start:
            self.speech_recognition.subscribe("SpeechHandler")
        else:
            self.speech_recognition.unsubscribe("SpeechHandler")

    # Listener
    # =========
    def on_speech_event(self, event_name=None, task_id=None, subscriber_identifier=None):
        self.logger.info("Speech Event: {} | {} | {}".format(event_name, task_id, subscriber_identifier))
        self.on_start_listening()

    def on_start_listening(self, results=None):
        self.is_listening = True
        self.add_keywords(keywords=self.current_keywords)
        self.keyword_stream(start=True)

    # ======
    # SPEECH
    # ======
    def say(self, message="Hi"):
        text = "\\vct={}\\\\rspd={}\\{}".format(int(self.voice_pitch), int(self.voice_speed), message)
        self.tts.say(text)

    def animated_say(self, message="", animation_name=None):
        text = "\\vct={}\\\\rspd={}\\{}".format(int(self.voice_pitch), int(self.voice_speed), message)
        if animation_name is None:
            self.animated_speech.say(text, {"bodyLanguageMode": "contextual"})  # vs random
        else:
            self.animated_speech.say('^start({}) {} ^wait({})'.format(animation_name, text, animation_name),
                                     {"bodyLanguageMode": "contextual"})

    def set_volume(self, level=50.0):
        vol = int(level) if level > 1 else int(level * 100)
        self.logger.info("Setting volume to: {}".format(vol))
        self.audio.setOutputVolume(vol)

    def set_language(self, name="English"):
        self.tts.setLanguage(name)
        self.speech_recognition.setLanguage(name)

    # MEMORY
    # ======
    def insert(self, data_dict=None):
        try:
            for key in data_dict.keys():
                self.memory.insertData(key, data_dict[key])
        except Exception as e:
            print("Error while inserting '{}' into memory: {}".format(data_dict, e))

    def raise_event(self, event_name, event_value):
        self.logger.info("Raised event '{}' to load '{}'".format(event_name, event_value))
        self.memory.raiseEvent(event_name, event_value)

    def get_speech_event(self):
        return self.memory.subscriber("ALAnimatedSpeech/EndOfAnimatedSpeech")

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
    def print_data(self, result):
        self.logger.info('Result received: {}'.format(result))
