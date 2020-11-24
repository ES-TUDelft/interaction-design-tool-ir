#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================ #
# ANIMATION_WORKER #
# ================ #
# Worker class for controlling the robot's animation
#
# @author ES
# **

import logging
import time

from autobahn.twisted import sleep
from twisted.internet.defer import inlineCallbacks

from es_common.enums.robot_enums import RobotLanguage
from es_common.model.interaction_block import InteractionBlock
from robot_manager.handler.irc.animation_handler import AnimationHandler
from robot_manager.handler.irc.speech_handler import SpeechHandler
from robot_manager.handler.irc.tablet_handler import TabletHandler
from robot_manager.worker.irc.irc_worker import IRCWorker


class AnimationWorker(IRCWorker):
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger("AnimationWorker")

        self.speech_handler = None
        self.tablet_handler = None
        self.animation_handler = None
        self.disengagement_interval = 10.0  # disengage after x seconds
        self.interaction_block = None

    """
    Override parent methods
    """

    @inlineCallbacks
    def on_connect(self, session, details=None):
        try:
            self.logger.debug("Received session: {}".format(session))

            if session is None:
                self.speech_handler = None
                self.animation_handler = None
                self.tablet_handler = None
            else:
                self.speech_handler = SpeechHandler(session=session)
                self.speech_handler.keyword_observers.add_observer(self.on_user_answer)

                self.tablet_handler = TabletHandler(session=session)
                self.tablet_handler.tablet_input_observers.add_observer(self.on_tablet_input)

                self.animation_handler = AnimationHandler(session=session)

                self._update_interaction_settings()

                # Start listening to DB Stream
                self.setup_db_stream()

                yield self.speech_handler.set_language(RobotLanguage.ENGLISH.value)
                yield self.speech_handler.animated_say("I am ready")

                self.logger.info("Connection to the robot is successfully established.")
        except Exception as e:
            yield self.logger.error("Error while setting the robot controller {}: {}".format(session, e))

    def _update_interaction_settings(self):
        # update speech certainty
        self.on_speech_certainty(data_dict=self.db_stream_controller.find_one(
            self.db_stream_controller.interaction_collection, "speechCertainty"))
        # update voice settings
        self.on_voice_pitch(data_dict=self.db_stream_controller.find_one(
            self.db_stream_controller.interaction_collection, "voicePitch"))
        self.on_voice_speed(data_dict=self.db_stream_controller.find_one(
            self.db_stream_controller.interaction_collection, "voiceSpeed"))
        # Disengagement
        self.on_disengagement_interval(data_dict=self.db_stream_controller.find_one(
            self.db_stream_controller.interaction_collection, "disengagementInterval"))

    def start_listening_to_db_stream(self):
        observers_dict = {
            "connectRobot": self.connect_robot,
            "disconnectRobot": self.disconnect_robot,
            "wakeUpRobot": self.on_wakeup,
            "restRobot": self.on_rest,
            "animateRobot": self.on_animate,
            "interactionBlock": self.on_interaction_block,
            "hideTabletImage": self.on_hide_tablet_image,
            "speechCertainty": self.on_speech_certainty,
            "voicePitch": self.on_voice_pitch,
            "voiceSpeed": self.on_voice_speed,
            "robotLanguage": self.on_robot_language,
            "disengagementInterval": self.on_disengagement_interval
        }
        # Listen to the "interaction_collection"
        self.db_stream_controller.start_db_stream(observers_dict=observers_dict,
                                                  db_collection=self.db_stream_controller.interaction_collection)

    """
    Class methods
    """

    def on_user_answer(self, val=None):
        try:
            self.logger.debug("User Answer: {}".format(val))

            self.on_block_executed(val=True, execution_result="" if val is None else val)
        except Exception as e:
            self.logger.error("Error while storing user answer: {}".format(e))

    def on_tablet_input(self, val=None):
        try:
            self.logger.debug("Tablet Input: {}".format(val))
            self.on_block_executed(val=True, execution_result=val)
            # self.db_stream_controller.update_one(self.db_stream_controller.robot_collection,
            #                               data_key="tabletInput",
            #                               data_dict={"tabletInput": val, "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while storing tablet input: {}".format(e))

    @inlineCallbacks
    def on_block_executed(self, val=None, execution_result=""):
        try:
            self.db_stream_controller.update_one(self.db_stream_controller.robot_collection, data_key="isExecuted",
                                                 data_dict={
                                                     "isExecuted": {"value": True, "executionResult": execution_result},
                                                     "timestamp": time.time()})
            yield sleep(1)
        except Exception as e:
            self.logger.error("Error while storing block completed: {}".format(e))

    @inlineCallbacks
    def on_wakeup(self, data_dict=None):
        self.logger.info("Waking up now!")
        yield self.animation_handler.wakeup()

    @inlineCallbacks
    def on_rest(self, data_dict=None):
        self.logger.info("Resting zzz")
        yield self.animation_handler.rest()

    @inlineCallbacks
    def on_animate(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))

            animation_name = data_dict["animateRobot"]["animation"]
            message = data_dict["animateRobot"]["message"]
            if message is None or message == "":
                yield self.animation_handler.execute_animation(animation_name=animation_name)
            else:
                yield self.speech_handler.animated_say(message=message)
        except Exception as e:
            self.logger.error("Error while extracting animate data: {} | {}".format(data_dict, e))

    def on_hide_tablet_image(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            pass
        except Exception as e:
            self.logger.error("Error while extracting tablet image: {} | {}".format(data_dict, e))

    @inlineCallbacks
    def on_interaction_block(self, data_dict=None):
        self.logger.info("Received Interaction Block data.\n")

        # check if is still engaged
        if not self.is_engaged():
            return self.on_disengagement()

        try:
            interaction_block = self.get_interaction_block(data_dict=data_dict)

            # execute the animation
            if interaction_block.animation is not None:
                yield self.animation_handler.execute_animation(interaction_block.animation)

            # get the message
            message = interaction_block.message
            if message is None or message == "":
                # reset web page
                if self.has_tablet():
                    self.set_web_view()
                self.on_block_executed(val=True)
            else:
                self.logger.info("Message to say: {}".format(message))
                if self.has_tablet():
                    self.set_web_view(tablet_page=interaction_block.tablet_page)

                speech_event = self.speech_handler.animated_say(message=message)
                self.logger.info("Speech Event: {}".format(speech_event))

                # check if user answers or tablet_input are needed
                if "input" in interaction_block.pattern.lower() and self.has_tablet():
                    self.logger.info("Wait for input from tablet...")
                    yield self.tablet_handler.input_stream(start=True)
                elif "question" in interaction_block.pattern.lower():
                    keywords = interaction_block.get_combined_answers()
                    self.speech_handler.current_keywords = keywords

                    yield speech_event.addCallback(self.speech_handler.on_start_listening)
                else:
                    # time.sleep(1)  # to keep the API happy :)
                    yield speech_event.addCallback(self.on_block_executed)
        except Exception as e:
            self.logger.error("Error while extracting interaction block: {} | {}".format(data_dict, e))
            self.on_block_executed()

    def on_disengagement(self):
        self.logger.info("User is disengaged... Stop interacting!")
        self.speech_handler.animated_say(message="Oops, looks like you left. Goodbye!")
        self.animation_handler.reset_posture()

        if self.has_tablet():
            self.tablet_handler.show_webview(hide=True)

        self.db_stream_controller.update_one(self.db_stream_controller.robot_collection,
                                             data_key="isDisengaged",
                                             data_dict={"isDisengaged": True, "timestamp": time.time()})

    def get_interaction_block(self, data_dict=None):
        if data_dict is None:
            return None

        try:
            block_dict = data_dict["interactionBlock"]
            interaction_block = InteractionBlock.create_interaction_block(block_dict)
            if interaction_block:
                self.logger.info("Block's execution is in progress...")

                interaction_block.id = block_dict["id"]
                interaction_block.is_hidden = True

            return interaction_block
        except Exception as e:
            self.logger.error("Error while creating the interaction block: {}".format(e))
            return None

    def set_web_view(self, tablet_page=None):
        try:
            if tablet_page is None:
                page_name = "index"
                url_params = ""
            else:
                page_name = tablet_page.name
                url_params = "?{}{}{}".format(self.check_url_parameter("pageHeading", tablet_page.heading),
                                              self.check_url_parameter("pageText", tablet_page.text),
                                              self.check_url_parameter("pageImage", tablet_page.image))

            self.logger.info("Setting the robot's tablet.")
            self.tablet_handler.show_webview(TabletHandler.create_tablet_url(page_name=page_name,
                                                                             url_params=url_params))
        except Exception as e:
            self.logger.error("Error while constructing the tablet URL: {}".format(e))

    def check_url_parameter(self, param_name, param_value):
        if param_value is not None and param_value != "":
            return "{}={}&".format(param_name, param_value)

        return ""

    def on_touch(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            # TODO
        except Exception as e:
            self.logger.error("Error while extracting touch data: {} | {}".format(data_dict, e))

    def on_speech_certainty(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.speech_handler.speech_certainty = data_dict["speechCertainty"]
        except Exception as e:
            self.logger.error("Error while extracting speech certainty data: {} | {}".format(data_dict, e))

    def on_voice_pitch(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.speech_handler.voice_pitch = data_dict["voicePitch"]
        except Exception as e:
            self.logger.error("Error while extracting voice pitch data: {} | {}".format(data_dict, e))

    def on_voice_speed(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.speech_handler.voice_speed = data_dict["voiceSpeed"]
        except Exception as e:
            self.logger.error("Error while extracting voice speed data: {} | {}".format(data_dict, e))

    def on_robot_language(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.speech_handler.set_language(name=RobotLanguage[data_dict["robotLanguage"].upper()].value)
        except Exception as e:
            self.logger.error("Error while extracting language data: {} | {}".format(data_dict, e))

    def on_disengagement_interval(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.disengagement_interval = data_dict["disengagementInterval"]
        except Exception as e:
            self.logger.error("Error while extracting speech certainty data: {} | {}".format(data_dict, e))

    def is_engaged(self):
        # TODO:
        #       - test whether the face_detection process is blocking the robot animation
        #       - in that case, provide a better solution!
        try:
            last_seen_data = self.db_stream_controller.find_one(self.db_stream_controller.robot_collection,
                                                                data_key="isEngaged")
            # last_seen = time.time() - last_seen_data["timestamp"]
            # self.logger.info("Last Seen: {:.2f}s | Disengage after: {}s\n".format(last_seen,
            #                                                                       self.disengagement_interval))
            # if last_seen <= self.disengagement_interval:
            #     return True
            return last_seen_data["isEngaged"]
        except Exception as e:
            self.logger.error("Error while fetching isEngaged data: {}".format(e))
            return True
