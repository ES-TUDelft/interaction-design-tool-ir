#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============== #
# TABLET_HANDLER #
# ============== #
# Handler class for controlling the robot's screen (tablet)
#
# @author ES
# **

import logging

from twisted.internet.defer import inlineCallbacks

from es_common.model.observable import Observable
from es_common.utils import config_helper


class TabletHandler(object):

    def __init__(self, session):

        self.logger = logging.getLogger("TabletHandler")
        self.session = session

        # add a listener to the tablet input stream
        self.session.subscribe(self.on_tablet_input, "rom.optional.tablet_input.stream")
        self.tablet_input_observers = Observable()
        self.is_listening = False

    def show_webview(self, url="https://www.google.com", hide=False):
        try:
            if hide is True:
                self.session.call("rom.optional.tablet.stop")
            else:
                self.session.call("rom.optional.tablet.view", url=url)
        except Exception as e:
            self.logger.error(e)

    def show_offline_page(self, name="index", url_params=None):
        try:
            tablet_settings = config_helper.get_tablet_settings()

            url = "http://{}/{}{}".format(tablet_settings["ip"], tablet_settings["pages"][name],
                                          "" if url_params is None else url_params)
            # self.logger.info("URL: {}".format(url))

            self.session.call("rom.optional.tablet.view", url=url)
        except Exception as e:
            self.logger.error("Error while setting offline tablet page: {} | {}".format(url_params, e))

    @inlineCallbacks
    def on_tablet_input(self, frame=None):
        if (not self.is_listening) and (frame is None or len(frame) == 0):
            self.logger.info("No frames!")
        else:
            try:
                self.logger.info("Received Tablet Input: {}".format(frame["data"]))
                self.is_listening = False
                yield self.input_stream(start=False)

                tablet_input = frame["data"]["body"]["text"]
                if type(tablet_input) is bytes:
                    tablet_input = tablet_input.decode('utf-8')

                yield self.show_offline_page()
                self.tablet_input_observers.notify_all(tablet_input)
            except Exception as e:
                self.logger.error("Error while getting the received tablet input: {}".format(e))
                yield False

    def input_stream(self, start=False):
        self.logger.info("{} Tablet Input stream.".format("Starting" if start else "Closing"))
        self.is_listening = start
        # start/close the input stream
        self.session.call("rom.optional.tablet_input.stream" if start else "rom.optional.tablet_input.close")

    def set_image(self, image_path="img/help_charger.png", hide=False):
        try:
            self.session.call("rom.optional.tablet.image", location=image_path, hide=hide)
        except Exception as e:
            self.logger.error(e)

    def configure_wifi(self, security="WPA2", ssid="wlan 3", key="liacs_8_"):
        try:
            self.session.call("rom.optional.tablet.wifi", security=security, ssid=ssid, key=key)
            self.logger.debug("Successfully configured the wifi.")
        except Exception as e:
            self.logger.error("Error while configuring the wifi! {}".format(e))
