#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============================== #
# UI_SPOTIFY_CONNECTION_CONTROLLER #
# ============================== #
# Class for controlling the connection to SPOTIFY.
#
# @author ES
# **
import json
import logging

import spotipy
from PyQt5 import QtWidgets, QtGui

import es_common.hre_config as pconfig
from interaction_manager.utils import config_helper
from interaction_manager.view.ui_spotify_dialog import Ui_SpotifyDialog


class UISpotifyConnectionController(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(UISpotifyConnectionController, self).__init__(parent)

        self.logger = logging.getLogger("UISpotifyConnection Controller")

        self.default_spotify_settings = config_helper.get_spotify_settings()

        self.username = None
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        self.spotify = None
        self.scope = "user-library-read, playlist-read-private, app-remote-control, streaming, " \
                     "user-read-playback-state, user-modify-playback-state"
        self.success = False
        self.playlists = {}
        # init UI elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        self.ui = Ui_SpotifyDialog()
        self.ui.setupUi(self)

        # connect listener
        self.ui.connectButton.clicked.connect(self.connect)
        self.ui.playButton.clicked.connect(self.play)

        self.ui.playlistComboBox.currentIndexChanged.connect(self.update_tracks_combo)
        self.ui.trackComboBox.currentIndexChanged.connect(self.enable_play_button)
        self.ui.defaultSettingsCheckBox.stateChanged.connect(self.enable_settings)

        self.repaint()

    def set_spotify_settings(self):
        if self.ui.defaultSettingsCheckBox.isChecked() is True:
            self.username = self.default_spotify_settings["username"]
            self.client_id = self.default_spotify_settings["client_id"]
            self.client_secret = self.default_spotify_settings["client_secret"]
            self.redirect_uri = self.default_spotify_settings["redirect_uri"]
        else:
            self.username = self.validate(val="{}".format(self.ui.usernameLineEdit.text()).strip(),
                                          default=self.default_spotify_settings["username"])
            self.client_id = self.validate(val="{}".format(self.ui.clientIDLineEdit.text()).strip(),
                                           default=self.default_spotify_settings["client_id"])
            self.client_secret = self.validate(val="{}".format(self.ui.clientSecretLineEdit.text()).strip(),
                                               default=self.default_spotify_settings["client_secret"])
            self.redirect_uri = self.validate(val="{}".format(self.ui.redirectURILineEdit.text()).strip(),
                                              default=self.default_spotify_settings["redirect_uri"])

    def validate(self, val, default):
        if val is None or val == "":
            return default
        return val

    def connect(self):
        self._display_message(message="Connecting...")
        self.set_spotify_settings()

        try:
            client_credentials_manager = spotipy.SpotifyOAuth(client_id=self.client_id,
                                                              client_secret=self.client_secret,
                                                              redirect_uri=self.redirect_uri,
                                                              scope=self.scope,
                                                              username=self.username)
            # spotipy.SpotifyClientCredentials(self.client_id, self.client_secret)
            self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            playlists = self.spotify.user_playlists(self.username, limit=5)

            if playlists is None or len(playlists["items"]) == 0:
                self._display_message(warning="*** Couldn't find any playlist! Please try with another username.")
            else:
                for playlist in playlists["items"]:
                    # if playlist['owner']['id'] == self.username:
                    self._display_message(message="Playlist '{}' has {} tracks".format(playlist["name"],
                                                                                       playlist["tracks"]["total"]))
                    results = self.spotify.playlist(playlist["id"], fields="tracks,next")
                    tracks = results["tracks"]
                    # self._display_message(message="{}".format(json.dumps(tracks, sort_keys=True, indent=4)))
                    tracks_dict = {}
                    for item in tracks["items"]:
                        track = item["track"]
                        # self._display_message(message="{}".format(json.dumps(track, sort_keys=True, indent=4)))
                        tracks_dict[track["name"]] = track["uri"]

                    self.playlists[playlist["name"]] = {
                        "id": playlist["id"],
                        "tracks": tracks_dict
                    }
            self.success = True
            self.update_playlist_combo()
            self._display_message(message="Successfully connected to spotify.")
            # self._display_message(message="{}".format(json.dumps(self.playlists, sort_keys=True, indent=4)))
            self.repaint()
        except Exception as e:
            self._display_message(error="Error while connecting to spotify! {}".format(e))
            self.ui.connectButton.setEnabled(True)
            self.success = False

    def update_playlist_combo(self):
        self.ui.playlistComboBox.clear()
        if self.playlists is None or len(self.playlists) == 0:
            return

        try:
            self.ui.playlistComboBox.addItems([pconfig.SELECT_OPTION])
            self.ui.playlistComboBox.addItems([p for p in self.playlists.keys()])
        except Exception as e:
            self._display_message(error="Error while loading tracks! {}".format(e))

    def update_tracks_combo(self):
        self.ui.trackComboBox.clear()
        playlist = self.ui.playlistComboBox.currentText()

        if playlist == "" or playlist == pconfig.SELECT_OPTION:
            return False
        try:
            self.ui.trackComboBox.addItems([pconfig.SELECT_OPTION])
            self.ui.trackComboBox.addItems([t for t in self.playlists[playlist]["tracks"]])
            return True
        except Exception as e:
            self._display_message(error="Error while loading tracks! {}".format(e))

    def enable_play_button(self):
        self.ui.playButton.setEnabled(True if self.ui.trackComboBox.currentText() != pconfig.SELECT_OPTION else False)

    def enable_settings(self, val):
        self.ui.settingsGroupBox.setEnabled(not self.ui.defaultSettingsCheckBox.isChecked())
        self.repaint()

    def has_active_device(self):
        devices = self.spotify.devices()
        # self._display_message(message="{}".format(json.dumps(devices, sort_keys=True, indent=4)))
        for device in devices["devices"]:
            if device["is_active"] is True:
                return True
        return False

    def play(self):
        try:
            if self.has_active_device() is False:
                self._display_message(message="There are no active devices!")
                return False

            is_playing = self.spotify.current_user_playing_track()["is_playing"]
            if is_playing is True:
                self.spotify.pause_playback()

            track_uri = self.get_track_uri()
            self._display_message(message="Playing: {}".format(self.ui.trackComboBox.currentText()))  # , track_uri))
            if track_uri is not None:
                self.spotify.start_playback(uris=[track_uri])

            return True
        except Exception as e:
            self._display_message("Error while playing! {}".format(e))

    def get_track_uri(self):
        playlist = self.ui.playlistComboBox.currentText()
        if playlist == pconfig.SELECT_OPTION:
            return None
        track = self.ui.trackComboBox.currentText()
        if track == pconfig.SELECT_OPTION:
            return None
        return self.playlists[playlist]["tracks"][track]

    def _display_message(self, message=None, error=None, warning=None):
        if error is not None:
            self.ui.messageTextEdit.setTextColor(QtGui.QColor('red'))  # red text for errors
            self.ui.messageTextEdit.append(error)
            self.logger.error(error)
        else:
            self.ui.messageTextEdit.setTextColor(QtGui.QColor("orange" if message is None else "white"))
            self.ui.messageTextEdit.append(warning if message is None else message)
            self.logger.info(warning if message is None else message)

        self.repaint()
