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

from es_common.utils import config_helper

TABLET_IP = "198.18.0.1"


class TabletHandler(object):

    def __init__(self, session):

        self.logger = logging.getLogger("TabletHandler")
        self.session = session

    def show_webview(self, url="https://www.google.com", hide=False):
        try:
            if hide is True:
                self.session.call("rom.optional.tablet.stop")
            else:
                self.session.call("rom.optional.tablet.view", url=url)
        except Exception as e:
            self.logger.error(e)

    def show_offline_page(self, name="index", params=None):
        # param is a dict
        url_params = ""
        try:
            if params and len(params) > 0:
                url_params = "?"
                for p in params:
                    if params[p] != "":
                        url_params = "{}{}={}&".format(url_params, p, params[p])
                # url_params = "?{}".format(urllib.parse.urlencode(params))

            tablet_pages = config_helper.get_tablet_settings()["pages"]

            url = "http://{}/{}{}".format(TABLET_IP, tablet_pages[name], url_params)
            self.logger.info("URL: {}".format(url))

            self.session.call("rom.optional.tablet.view", url=url)
        except Exception as e:
            self.logger.error("Error while setting offline tablet page: {} | {}".format(params, e))

    def set_image(self, image_path="img/help_charger.png", hide=False):
        try:
            pass
            # self.session.call("rom.optional.tablet.image", location=image_path, hide=hide)
        except Exception as e:
            self.logger.error(e)

    def load_application(self, app_name):
        if app_name is None:
            return

        try:
            # self.session.call("rom.optional.tablet.load", app_name=app_name)
            self.logger.info("Successfully loaded '{}'".format(app_name))
        except Exception as e:
            self.logger.info("Error while loading {}. {}".format(app_name, e))

    def configure_wifi(self, security="WPA2", ssid="wlan 3", key="liacs_8_"):
        try:
            # self.session.call("rom.optional.tablet.wifi", security=security, ssid=ssid, key=key)
            self.logger.debug("Successfully configured the wifi.")
        except Exception as e:
            self.logger.error("Error while configuring the wifi! {}".format(e))

    def insert(self, data_dict=None):
        if data_dict is None:
            return
        try:
            pass
            # self.session.call("rom.optional.tablet.insert", data_dict=data_dict)
        except Exception as e:
            self.logger.error("Error while inserting '{}' into memory: {}".format(data_dict, e))
