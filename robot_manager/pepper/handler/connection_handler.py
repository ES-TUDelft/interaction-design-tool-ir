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
import threading

from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

import es_common.utils.config_helper as config_helper
from es_common.model.observable import Observable


class ConnectionHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("Connection Handler")
        self.rie = None
        self.session_observers = Observable()

    @inlineCallbacks
    def on_connected(self, session, details=None):
        self.logger.debug("Created session: {}".format(session))
        yield self.session_observers.notify_all(session)

    def start_rie_session(self, robot_name=None, robot_realm=None):
        try:
            if robot_realm is None:
                # get the realm from config
                name_key = "pepper" if robot_name is None else robot_name.name.lower()
                robot_realm = config_helper.get_robot_settings()["realm"][name_key]
            self.logger.info("{} REALM: {}\n".format(robot_name, robot_realm))

            self.rie = Component(
                transports=[{
                    'url': u"wss://wamp.robotsindeklas.nl",
                    'serializers': ['msgpack'],
                    'max_retries': 0
                }],

                realm=robot_realm
            )
            self.logger.info("** {}\n\n".format(threading.current_thread().name))
            self.rie.on_join(self.on_connected)

            self.logger.info("Running the rie component")
            run([self.rie])
        except Exception as e:
            self.logger.error("Unable to run the rie component | {}".format(e))
