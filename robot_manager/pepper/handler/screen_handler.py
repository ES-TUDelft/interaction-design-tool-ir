#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============== #
# SCREEN_HANDLER #
# ============== #
# Handler class for controlling the robot's screen (tablet)
#
# @author ES
# **

import logging

import es_common.hre_config as pconfig


class ScreenHandler(object):

    def __init__(self, session):

        self.logger = logging.getLogger("ScreenHandler")

        self.robot_screen = session.service("ALTabletService")

        # self.configure_wifi()
        # self.set_webview(hide=False

    def set_webview(self, webpage="http://www.google.com", hide=False):
        try:
            if hide is True:
                self.robot_screen.hideWebview()
            else:
                # Enable tablet wifi and display the webpage
                self.robot_screen.enableWifi()
                self.robot_screen.showWebview(webpage)
        except Exception as e:
            self.logger.error(e)

    def set_image(self, image_path="/img/help_charger.png", hide=False):
        # If hide is false, display a local image located in img folder in the root of the robot
        full_path = "http://{}/{}".format(pconfig.robot_tablet_ip, image_path)
        self.logger.info("Image path: {}".format(full_path))
        try:
            self.robot_screen.hideImage() if hide is True else self.robot_screen.showImageNoCache(
                full_path)  # .showImage(full_path)
            # self.robot_screen.showImageNoCache('http://' + pconfig.robot_tablet_ip + '/' + image_path)
        except Exception as e:
            self.logger.error(e)

    def load_application(self, app_name):
        if app_name is None: return

        try:
            self.robot_screen.loadApplication(app_name)
            self.robot_screen.showWebview()
            self.logger.info("Successfully loaded '{}'".format(app_name))
        except Exception as e:
            self.logger.info("Error while loading {}. {}".format(app_name, e))

    def configure_wifi(self, security="WPA2", ssid="wlan 3", key="liacs_8_"):
        try:
            self.robot_screen.configureWifi(security, ssid, key)
            self.logger.debug("Successfully configured the wifi.")
        except Exception as e:
            self.logger.error("Error while configuring the wifi! {}".format(e))
