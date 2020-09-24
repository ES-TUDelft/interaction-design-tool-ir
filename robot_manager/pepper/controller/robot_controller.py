#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================ #
# ROBOT_CONTROLLER #
# ================ #
# Class for controlling the robot.
#
# @author ES
# **

import logging
import time

import es_common.hre_config as pconfig
from es_common.enums.led_enums import LedColor
from es_common.enums.robot_name import RobotName
from es_common.model.observable import Observable
from es_common.utils.timer_helper import TimerHelper
from robot_manager.pepper.enums.sensor_enums import Sonar, LedName
from robot_manager.pepper.enums.tablet_enums import TabletAction
from robot_manager.pepper.handler.animation_handler import AnimationHandler
from robot_manager.pepper.handler.engagement_handler import EngagementHandler
from robot_manager.pepper.handler.sensor_handler import SensorHandler
from robot_manager.pepper.handler.speech_handler import SpeechHandler
from robot_manager.pepper.handler.tablet_handler import TabletHandler


class RobotController(object):

    def __init__(self, robot_name=RobotName.PEPPER.name):
        self.logger = logging.getLogger("RobotController")

        self.robot_name = robot_name
        self.last_time_touched = 0
        self.timer_helper = TimerHelper()

        self.is_interacting = False
        self.is_in_engagement_mode = False
        self.animation_handler, self.sensor_handler, self.engagement_handler = (None,) * 3
        self.speech_handler, self.tablet_handler = (None,) * 2

        self.session = None
        self.is_engaged_observers = Observable()

    def set_session(self, session):
        try:
            self.session = session
            self.logger.info("Received session: {}".format(self.session))

            self._init_handlers()

            self.speech_handler.set_language("en")
            self.speech_handler.animated_say("I am ready")
        except RuntimeError as e:
            self.logger.error("Error while setting the session | ".format(e))

    def _init_handlers(self):
        self.animation_handler = AnimationHandler(session=self.session)
        self.speech_handler = SpeechHandler(session=self.session)
        if self.robot_name.lower() == RobotName.PEPPER.name.lower():
            self.tablet_handler = TabletHandler(session=self.session)
        self.sensor_handler = SensorHandler(session=self.session)
        self.engagement_handler = EngagementHandler(session=self.session)

    """
    TOUCH EVENTS
    """

    def subscribe_to_touch_events(self):
        pass
        # self.touch = self.sensor_handler.memory.subscriber("TouchChanged")

    def react_to_touch(self, message, led_name):
        self.sensor_handler.set_leds(led_name=led_name, led_color=LedColor.RED)
        self.complain(message=message)
        self.sensor_handler.set_leds(led_name=led_name, led_color=LedColor.WHITE)

    def touch(self):
        self.subscribe_to_touch_events()
        # TODO:
        #  self.robot_id = self.pepper_robot.touch.signal.connect(functools.partial(self.on_touch, "TouchChanged"))
        self.last_time_touched = time.time()
        self.logger.info("Touch is enabled")

    def on_touch(self, event_name, value):
        pass

    """
    DIALOG EVENTS
    """

    def observe_interaction_events(self, block_completed_callback, keyword_callback):
        self.speech_handler.block_completed_observers.add_observer(block_completed_callback)
        self.speech_handler.keyword_observers.add_observer(keyword_callback)

    def observe_engagement_events(self, observer):
        self.is_engaged_observers.add_observer(observer=observer)

    """
    Motion control methods
    """

    def posture(self, wakeup=False, reset=False):
        result = False
        try:
            if reset is True:
                self.animation_handler.reset_posture()
            else:
                self.animation_handler.wakeup() if wakeup is True else self.animation_handler.rest()
        except Exception as e:
            self.logger.error("Error while changing Pepper's posture | {}".format(e))
        finally:
            return result

    def execute_animation(self, animation_name):
        self.animation_handler.execute_animation(animation_name=animation_name)

    def move_to(self, x=0, y=0, theta=0):
        self.animation_handler.move_to(x=x, y=y, theta=theta)

    def is_awake(self):
        return self.animation_handler.is_awake()

    """
    ENGAGEMENT
    """

    def engagement(self, start=True):
        if start is True:
            # self.is_engaged_signal = is_engaged_signal
            self.is_in_engagement_mode = True
            self.logger.info("Engagement is set.")
            self.subscribe_to_engagement_events(subscribe=True)
        else:
            self.is_in_engagement_mode = False
            self.subscribe_to_engagement_events(subscribe=False)
            self.posture(reset=True)
            # self.stop_dialog()
            self.logger.info("Engagement is disabled")

    def subscribe_to_engagement_events(self, subscribe=True):
        # TODO
        if subscribe is True:
            self.engage()
        else:
            self.logger.info("Unsubscribed from engagement events.")

    def engage(self):
        # self.engagement_handler.set_engagement(EngagementMode.FULLY_ENGAGED)
        # self.engagement_handler.engage(self.pid)
        if self.is_interacting is False:
            self.logger.info("Robot is ready to engage.")
            self.is_engaged_observers.notify_all(True)
            # self.is_engaged_signal.emit(True)
        else:
            self.logger.info("Re-engaging...")

    def face_detection(self, start=False):
        self.engagement_handler.face_detection(start=start)

    def update_speech_certainty(self, speech_certainty=None):
        if self.speech_handler and speech_certainty is not None:
            self.speech_handler.speech_certainty = speech_certainty

    """
    Speech control methods
    """

    def say(self, message=""):
        self.speech_handler.say(message=message)

    def animated_say(self, message=None, animation_name=None):
        self.speech_handler.animated_say(message=message, animation_name=animation_name)

    def customized_say(self, interaction_block=None):
        # update the html page fields
        self.load_html_page(interaction_block.tablet_page)

        # say the message
        self.speech_handler.customized_say(interaction_block=interaction_block)

    def set_volume(self, level=50.0):
        self.speech_handler.set_volume(level=level)

    def set_language(self, language="en"):
        self.speech_handler.set_language(name=language)
        time.sleep(1.0)
        self.logger.info("Language set to '{}'".format(language))

    def complain(self, message="Hey"):
        self.animated_say(message=message)
        self.posture(reset=True)

    """
    Tablet control methods
    """

    def tablet_image(self, hide=False, action_name=TabletAction.IMAGE, action_url=pconfig.welcome_image):
        if self.tablet_handler is None:
            return
        try:
            if action_name is TabletAction.IMAGE:
                self.tablet_handler.set_image(image_path=action_url, hide=hide)
            elif action_name is TabletAction.WEBVIEW:
                self.tablet_handler.show_webview(url=action_url, hide=hide)
        except Exception as e:
            self.logger.error("Error while setting the tablet: {}".format(e))

    def load_application(self, app_name):
        if self.tablet_handler is not None:
            self.tablet_handler.load_application(app_name)

    def load_html_page(self, tablet_page=None):
        if self.tablet_handler is None or tablet_page is None:
            return

        params = {
            "pageHeading": "{}".format(tablet_page.heading),
            "pageText": "{}".format(tablet_page.text),
            "pageImage": "{}".format("pepper-standing.png" if tablet_page.image is None else tablet_page.image)
        }
        self.tablet_handler.show_offline_page(name=tablet_page.name, params=params)

    """
    LED CONTROL
    """

    def set_leds(self, led_name=LedName.FACE, led_color=LedColor.WHITE, duration=0.5):
        self.sensor_handler.set_leds(led_name=led_name, led_color=led_color, duration=duration)

    """
    SENSOR ACCESS
    """

    def distance(self, sonar=Sonar.FRONT):
        return self.sensor_handler.get_distance(sonar=sonar)
