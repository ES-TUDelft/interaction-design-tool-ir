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
    def create_qi_session(robot_ip, robot_port):
        session = None
        try:
            session = qi.Session()
            session.connect("tcp://{}:{}".format(robot_ip, robot_port))

            ConnectionHandler.logger.info("Successfully connected to robot:\n- IP: {} | Port: {}".format(
                robot_ip, robot_port))
        except RuntimeError as e:
            session = None
            ConnectionHandler.logger.error("Unable to connect to robot using:\n- IP: {} | Port: {}\n{}".format(
                robot_ip, robot_port, e))
        finally:
            return session

    @staticmethod
    def create_qi_app(name, robot_ip, robot_port=9559):
        app = None
        try:
            app = qi.Application([name, "--qi-url=tcp://{}:{}".format(robot_ip, robot_port)])
            ConnectionHandler.logger.info("Successfully connected to Robot")
        except RuntimeError as e:
            ConnectionHandler.logger.error("Error while creating qi application: {}".format(e))
        finally:
            return app
