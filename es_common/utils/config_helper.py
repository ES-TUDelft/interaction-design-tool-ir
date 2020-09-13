import os
import logging
import yaml


def _setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger('ESCommon Config')


logger = _setup_logger()


####
# Config
###
def _get_config():
    config = None
    try:
        with open("es_common/properties/config.yaml", 'r') as yaml_file:
            config = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Error while opening the config file! {}".format(e))
    finally:
        return config


sys_config = _get_config()


####
# TABLE BOOKER
###
def get_table_booker_settings():
    table_booker = None
    try:
        # check if there is a config file for table_booker, otherwise use default config
        file_path = "es_common/properties/tablebooker.yaml"
        if os.path.isfile(file_path) is True:
            logger.debug("Found TableBooker config file")
            with open(file_path, 'r') as yaml_file:
                config = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        else:
            logger.debug("Couldn't find a TableBooker config file! Using default config instead.")
            config = sys_config

        table_booker = config["table_booker"]
    except Exception as e:
        logger.error("Error while loading TableBooker config! {}".format(e))
    finally:
        return table_booker


####
# ROBOT SETTINGS
###
def get_robot_settings():
    robot_settings = None
    try:
        # check if there is a config file for table_booker, otherwise use default config
        file_path = "es_common/properties/robot.yaml"
        if os.path.isfile(file_path) is True:
            logger.debug("Found robot config file")
            with open(file_path, 'r') as yaml_file:
                config = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        else:
            logger.debug("Couldn't find a robot config file! Using default config instead.")
            config = sys_config

        robot_settings = config["robot"]
    except Exception as e:
        logger.error("Error while loading TableBooker config! {}".format(e))
    finally:
        return robot_settings
