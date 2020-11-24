#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============== #
# TABLET_HANDLER #
# ============== #
# Handler class for controlling the robot's tablet
#
# @author ES
# **

import logging

from es_common.model.observable import Observable
from es_common.utils import config_helper


class TabletHandler(object):

    def __init__(self, session):

        self.logger = logging.getLogger("TabletHandler")
        self.session = session

        self.tablet_service = self.session.service("ALTabletService")
        self.memory = self.session.service("ALMemory")

        # TODO: add a listener to the tablet input stream
        self.tablet_input_listener = self.memory.subscriber("TabletInput")
        self.tablet_input_listener.signal.connect(self.on_tablet_input)

        self.tablet_input_observers = Observable()
        self.is_listening = False

    def show_webview(self, url="https://www.google.com", hide=False):
        try:
            if hide is True:
                self.tablet_service.hideWebview()
            else:
                # Enable tablet wifi and display the webpage
                self.tablet_service.enableWifi()
                self.tablet_service.showWebview(url)
        except Exception as e:
            self.logger.error(e)

    def on_tablet_input(self, value=None):
        self.logger.info("Tablet Input: {}".format(value))
        if not self.is_listening:
            self.logger.info("Not listening!")
        elif not value:
            self.logger.info("No input received!")
        else:
            try:
                self.logger.info("Received Tablet Input: {}".format(value))
                self.is_listening = False
                self.input_stream(start=False)

                tablet_input = value
                if type(tablet_input) is bytes:
                    tablet_input = tablet_input.decode('utf-8')

                url = TabletHandler.create_tablet_url(page_name="index")

                self.show_webview(url=url)
                self.tablet_input_observers.notify_all(tablet_input)
            except Exception as e:
                self.logger.error("Error while getting the received tablet input: {}".format(e))

    def input_stream(self, start=False):
        self.logger.info("{} Tablet Input stream.".format("Starting" if start else "Closing"))
        self.is_listening = start
        # TODO: start/close the input stream

    @staticmethod
    def create_tablet_url(page_name="index", url_params=None):
        tablet_settings = config_helper.get_tablet_settings()
        url = "http://{}/{}{}".format(tablet_settings["ip"], tablet_settings["pages"]["{}".format(page_name)],
                                      "" if url_params is None else url_params)
        return url

    def set_image(self, image_path="img/help_charger.png", hide=False):
        # If hide is false, display a local image located in img folder in the root of the robot
        tablet_settings = config_helper.get_tablet_settings()
        full_path = "http://{}/{}".format(tablet_settings["ip"], image_path)
        self.logger.info("Image path: {}".format(full_path))

        try:
            self.tablet_service.hideImage() if hide is True else self.tablet_service.showImageNoCache(full_path)
        except Exception as e:
            self.logger.error("Error while setting tablet image: {}".format(e))

    def configure_wifi(self, security="WPA2", ssid="", key=""):
        try:
            self.tablet_service.configureWifi(security, ssid, key)
            self.logger.debug("Successfully configured the wifi.")
        except Exception as e:
            self.logger.error("Error while configuring the wifi! {}".format(e))
