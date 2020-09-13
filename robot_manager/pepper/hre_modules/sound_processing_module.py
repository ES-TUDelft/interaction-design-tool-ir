#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================= #
# SOUND_PROCESSING_MODULE #
# ======================= #
# Module for receiving sound from the robot's microphones
#
# @author ES
# **

import logging
import functools
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
from Queue import Queue  # Python 2 import
import speech_recognition as sr
import es_common.hre_config as pconfig
from robot_manager.pepper.utils import math_helper
import StringIO

MODULE_NAME = "SoundProcessingModule"
LISTEN_COUNT = 15


class SoundProcessingModule(object):
    """
    A module for receiving and processing the sound from the robot's front mic
    """

    def __init__(self, session):
        super(SoundProcessingModule, self).__init__()
        self.session = session
        self.peak = pconfig.sound_peak

        # Get the service ALAudioDevice.
        self.audio_service = self.session.service("ALAudioDevice")
        self.logger = logging.getLogger("SoundProcessingModule")
        self.micFront = []
        self.module_name = MODULE_NAME
        self.audio_queue = Queue()
        self.speech_recognizer = sr.Recognizer()
        self.observers = []
        self.listening_count = 0
        self.recording_in_progress = False
        self.pause_sound_processing = False
        self.previous_sound_data = None
        self.outfile = None

    def notify_observers(self, outfile=None, is_recording=False):
        """
        Notify observers that an audio is received
        """
        for observer in self.observers:
            observer.process_sound(audio=outfile, is_recording=is_recording)

    def start_processing(self):
        """
        Start processing
        """
        # ask for the front microphone signal sampled at 16kHz
        # if you want the 4 channels call setClientPreferences(self.module_name, 48000, 0, 0)
        self.audio_service.setClientPreferences(self.module_name, 16000, 3, 0)
        self.audio_service.subscribe(self.module_name)
        self.logger.info("Starting Sound Processing")

    def stop_processing(self):
        """
        Stop processing
        """
        self.audio_service.unsubscribe(self.module_name)
        self.audio_queue.join()  # block until all jobs are done
        self.audio_queue = Queue()  # reset queue
        self.logger.info("Stopped sound processing")

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Get sound from front mic.
        This method is called automatically by the audio service
        (Do not change the name nor the signature)
        """
        if self.pause_sound_processing is False:
            peak_value, sound_data = math_helper.get_peak_and_sound_data(inputBuffer, nbOfChannels,
                                                                              nbOfSamplesByChannel)

            # Stop recording after some silence
            if self.listening_count <= 0 and self.recording_in_progress is True:
                self.stop_recording()

            # Recording in progress
            if self.recording_in_progress is True:
                self.listening_count = self.listening_count - 1
                self.outfile.write(sound_data[0].tostring())

            # Check the peak and start recording, if needed
            if peak_value > self.peak:
                self.logger.info("PEAK: {}".format(peak_value))
                self.listening_count = LISTEN_COUNT
                if self.recording_in_progress is False:
                    self.start_recording(sound_data)

    def start_recording(self, sound_data):
        self.outfile = StringIO.StringIO()
        self.recording_in_progress = True
        self.notify_observers(is_recording=True)
        if sound_data is not None:
            self.outfile.write(sound_data[0].tostring())
        self.logger.info("Started recording...")

    def stop_recording(self):
        self.logger.info("Stopped recording...")
        self.recording_in_progress = False
        self.previous_sound_data = None
        self.outfile.seek(0)
        self.notify_observers(outfile=self.outfile, is_recording=False)

    def set_sound_peak(self, peak=pconfig.sound_peak):
        if peak < 0: return
        self.peak = peak
