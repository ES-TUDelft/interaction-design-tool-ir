#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================== #
# CONNECTION_HANDLER #
# ================== #
# Handler class for controlling the connection to the robot
#
# @author ES
# **

import logging
import qi


class ConnectionHandler(object):
    logger = logging.getLogger("Connection Handler")

    @staticmethod
    def create_qi_session(robot_ip, port):
        session = None
        try:
            session = qi.Session()
            session.connect("tcp://{}:{}".format(robot_ip, port))

            ConnectionHandler.logger.info("Successfully connected to Pepper:\n- IP: {} | Port: {}".format(
                robot_ip, port))
        except RuntimeError as e:
            session = None
            ConnectionHandler.logger.error("Unable to connect to Naoqi:\n- IP: {} | Port: {}\n{}".format(
                robot_ip, port, e))
        finally:
            return session
