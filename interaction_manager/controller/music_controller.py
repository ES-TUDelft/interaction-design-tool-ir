import logging


class MusicController(object):
    def __init__(self):

        self.logger = logging.getLogger("MusicController")
        self.spotify = None
        self.username = None
        self.playlists = None

        self.warning_message = None
        self.error_message = None

    def has_active_device(self):
        devices = self.spotify.devices()
        for device in devices["devices"]:
            if device["is_active"] is True:
                return True
        return False

    def pause(self):
        try:
            is_playing = self.spotify.current_user_playing_track()["is_playing"]
            if is_playing is True:
                self.spotify.pause_playback()
            return True
        except Exception as e:
            self.logger.error("Error while pausing the player! {}".format(e))
            return False

    def play(self, playlist, track):
        self.warning_message = None
        if playlist is None or track is None:
            return False

        try:
            if self.has_active_device() is False:
                self.warning_message = "There are no active devices!"
                self.logger.warning(self.warning_message)
                return False

            track_uri = self.get_track_uri(playlist, track)
            if track_uri is None:
                self.warning_message = "Couldn't find the track to play!"
                self.logger.warning(self.warning_message)
            else:
                self.logger.debug("Currently playing: {}".format(track))
                self.spotify.start_playback(uris=[track_uri])

            return True
        except Exception as e:
            self.logger.error("Error while playing {}! {}".format(track, e))
            self.warning_message = "Player not available!"
            self.error_message = e

    def volume(self, val):
        try:
            self.spotify.volume(val)
        except Exception as e:
            self.logger.error("Error while setting the device volume to {}! {}".format(val, e))
            self.error_message = e
            self.warning_message = "There are no active devices!"

    def get_track_uri(self, playlist, track):
        if playlist is None or track is None:
            return None

        track_uri = None
        try:
            track_uri = self.playlists[playlist]["tracks"][track]
        except Exception as e:
            self.logger.error("Error while getting the track uri! {} | {} | {}".format(playlist, track, e))
        finally:
            return track_uri
