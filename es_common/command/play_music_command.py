#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =================== #
# MUSIC_COMMAND #
# =================== #
# Command for music player actions.
#
# @author ES
# **
import logging
from collections import OrderedDict

from es_common.command.es_command import ESCommand
from es_common.enums.command_enums import ActionCommand


class PlayMusicCommand(ESCommand):
    def __init__(self, playlist=None, track=None, play_time=-1, animations_key=""):
        super(PlayMusicCommand, self).__init__(is_speech_related=False)

        self.logger = logging.getLogger("PlayMusic Command")
        self.command_type = ActionCommand.PLAY_MUSIC
        self.music_controller = None
        self.playlist = playlist
        self.track = track
        self.play_time = play_time  # -1 for playing the whole track
        self.animations_key = animations_key

    # =======================
    # Override Parent methods
    # =======================
    def clone(self):
        return PlayMusicCommand(playlist=self.playlist, track=self.track,
                                play_time=self.play_time, animations_key=self.animations_key)

    def reset(self):
        # TODO: reset the timer
        return "Not Implemented!"

    def execute(self):
        if self.music_controller is None or self.track is None:
            return False

        return self.music_controller.play(playlist=self.playlist, track=self.track)

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("command_type", self.command_type.name),
            ("playlist", self.playlist),
            ("track", self.track),
            ("play_time", self.play_time),
            ("animations_key", self.animations_key)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        self.playlist = data["playlist"]
        self.track = data["track"]

        self.play_time = data["play_time"] if "play_time" in data.keys() else -1
        self.animations_key = data["animations_key"] if "animations_key" in data.keys() else ""

        return True
