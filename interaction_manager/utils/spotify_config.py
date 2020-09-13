import logging

import spotipy

from interaction_manager.utils import config_helper

logger = logging.getLogger("Spotify Config")

default_spotify_settings = config_helper.get_spotify_settings()

scope = "user-library-read, playlist-read-private, app-remote-control, streaming, " \
        "user-read-playback-state, user-modify-playback-state"
username = default_spotify_settings["username"]
client_id = default_spotify_settings["client_id"]
client_secret = default_spotify_settings["client_secret"]
redirect_uri = default_spotify_settings["redirect_uri"]


def connect():
    logger.info("Connecting...")

    try:
        client_credentials_manager = spotipy.SpotifyOAuth(client_id=client_id,
                                                          client_secret=client_secret,
                                                          redirect_uri=redirect_uri,
                                                          scope=scope,
                                                          username=username)

        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        playlists = spotify.user_playlists(username, limit=5)

        if playlists is None or len(playlists["items"]) == 0:
            logger.warning("*** Couldn't find any playlist! Please try with another username.")
        else:
            for playlist in playlists["items"]:
                # if playlist['owner']['id'] == self.username:
                logger.info("Playlist '{}' has {} tracks".format(playlist["name"], playlist["tracks"]["total"]))

        logger.info("Successfully connected to spotify.")
    except Exception as e:
        logger.error("Error while connecting to spotify! {}".format(e))


connect()
