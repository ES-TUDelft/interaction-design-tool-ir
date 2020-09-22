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
import os
from collections import OrderedDict

import yaml


def _setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger('Config Logger')


logger = _setup_logger()


####
# APP PROPERTIES
###
def _get_app_properties():
    props = None
    try:
        with open("interaction_manager/properties/app.yaml", 'r') as ymlfile:
            props = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the app properties file! {}".format(e))
    finally:
        return props


app_properties = _get_app_properties()


def get_tags():
    # returns dict of gestures:
    # names are the keys and path are values
    return _get_property(_get_app_properties(), "tags")


def get_tablet_properties():
    tablet = []
    try:
        with open("es_common/properties/tablet.yaml", 'r') as ymlfile:
            props = yaml.load(ymlfile, Loader=yaml.SafeLoader)
            tablet = props["tablet"]
    except Exception as e:
        logger.error("Error while opening the app properties file! {}".format(e))
    finally:
        return tablet


####
# MONGO DB PROPERTIES
###
def _get_db_properties():
    props = None
    try:
        with open("interaction_manager/properties/db.yaml", 'r') as ymlfile:
            props = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the db properties file! {}".format(e))
    finally:
        return props


db_properties = _get_db_properties()


def get_db_mongo_settings():
    # returns dict of gestures: 
    # names are the keys and path are values
    return _get_property(db_properties, 'mongodb')


####
# Patterns
###
def _get_patterns_properties():
    patt = None
    try:
        with open("interaction_manager/properties/patterns.yaml", 'r') as yaml_file:
            patt = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the patterns properties file! {}".format(e))
    finally:
        return patt


_patterns = _get_patterns_properties()


def get_patterns():
    return _get_patterns_properties()


####
# BEHAVIORS PROPERTIES
###
def _get_behaviors_properties():
    props = None
    try:
        with open("interaction_manager/properties/behaviors.yaml", 'r') as ymlfile:
            props = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the behaviors properties file! {}".format(e))
    finally:
        return props


behaviors_properties = _get_behaviors_properties()


def get_gestures():
    # returns dict of gestures: 
    # names are the keys and path are values
    return _get_property(behaviors_properties, 'gestures')


###
# ANIMATIONS
###
def get_animations():
    animations_dict = OrderedDict()
    try:
        # with open('interaction_manager/properties/animations.json') as anim_file:
        #    animations_dict.update(json.load(anim_file))
        with open("interaction_manager/properties/animations.yaml", 'r') as ymlfile:
            animations_dict = ordered_yaml(ymlfile, yaml_loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the behaviors properties file! {}".format(e))
    finally:
        return animations_dict


def ordered_yaml(data_stream, yaml_loader, hook=OrderedDict):
    """
    :param data_stream:
    :param yaml_loader:
    :param hook:
    :return: ordered dict of the data stream from yaml file
    """

    class YamlOrderedLoader(yaml_loader):
        pass

    def create_mapping(loader, node):
        loader.flatten_mapping(node)
        return hook(loader.construct_pairs(node))

    YamlOrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, create_mapping
    )

    return yaml.load(data_stream, YamlOrderedLoader)


####
# Config
###
def _get_config():
    config = None
    try:
        with open("interaction_manager/properties/config.yaml", 'r') as yaml_file:
            config = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the config file! {}".format(e))
    finally:
        return config


sys_config = _get_config()


####
# SPOTIFY
###
def _get_spotify_config():
    spotify = None
    try:
        # check if there is a config file for spotify, otherwise use default config
        file_path = "interaction_manager/properties/spotify.yaml"
        if os.path.isfile(file_path) is True:
            logger.debug("Found spotify config file")
            with open(file_path, 'r') as yaml_file:
                config = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        else:
            logger.debug("Couldn't find a spotify config file! Using default config instead.")
            config = sys_config

        spotify = config["spotify"]
    except Exception as e:
        logger.error("Error while loading spotify config! {}".format(e))
    finally:
        return spotify


# TODO: remove
spotify_config = _get_spotify_config()


def get_spotify_settings():
    return _get_spotify_config()


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
