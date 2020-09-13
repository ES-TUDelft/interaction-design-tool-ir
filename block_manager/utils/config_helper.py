#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========================= #
# CONFIG_HELPER #
# ========================= #
# Helper class for accessing the app config.
#
# @author ES
# **

import logging
import sys

import yaml
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication


def _setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger('Block Config Logger')


logger = _setup_logger()


####
# Block Properties
###
def _get_block_properties():
    props = None
    try:
        # on Linux use: block-linux.yaml
        filename = "block.yaml"
        # if "linux" in sys.platform:  # for Mac: darwin | for windows: win32
        #    filename = "block-linux.yaml"

        with open("block_manager/properties/{}".format(filename), 'r') as yaml_file:
            props = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the block properties file! {}".format(e))
    finally:
        return props


block_props = _get_block_properties()


def get_colors():
    return block_props["colors"]


def get_icons():
    return block_props["icons"]


def get_block_mimetype():
    return block_props["block_mimetype"]


def get_history_limit():
    return block_props["history_limit"]


def get_block_size_settings():
    return block_props["size"]["block"]


def get_socket_size_settings():
    return block_props["size"]["socket"]


###
# STYLESHEET
###
def load_stylesheet():
    try:
        filename = "block_manager/qss/blockstyle-linux.qss"
        if "darwin" in sys.platform:  # for Mac: darwin | for windows: win32 | for Linux: linux
            filename = "block_manager/qss/blockstyle.qss"

        with open(filename, 'r') as stylesheet:
            QApplication.instance().setStyleSheet(stylesheet.read())
    except Exception as e:
        logger.error("Error while reading the stylesheet file! {}".format(e))


def get_block_title_font():
    if "darwin" in sys.platform:
        return QFont("Courier", 14, QFont.Bold)

    return QFont("Courier", 10, QFont.Bold)


###
# HELPER METHODS
###
def _get_property(props_dict, key):
    prop = None
    try:
        prop = props_dict[key]
    except Exception as e:
        logger.error("Error while getting '{}' from '{}' | {}".format(key, props_dict, e))
    finally:
        return prop
