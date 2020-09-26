import logging
import time

from twisted.internet.defer import inlineCallbacks

from es_common.model.interaction_block import InteractionBlock
from es_common.utils.db_helper import DBHelper
from robot_manager.pepper.controller.robot_controller import RobotController
from robot_manager.pepper.handler.connection_handler import ConnectionHandler
from thread_manager.db_thread import DBChangeStreamThread


class RobotWorker(object):
    def __init__(self, robot_name=None, robot_realm=None):
        self.logger = logging.getLogger("RobotWorker")

        self.robot_name = robot_name
        self.robot_realm = robot_realm

        self.db_helper = DBHelper()
        self.db_change_thread = None

        self.robot_controller = None
        self.connection_handler = None
        self.interaction_block = None

    def connect_robot(self, data_dict=None):
        try:
            self.connection_handler = ConnectionHandler()
            # self.connection_handler.session_observers.add_observer(self.on_connect)

            self.logger.info("Connecting...")
            self.connection_handler.start_rie_session(robot_name=self.robot_name,
                                                      robot_realm=self.robot_realm,
                                                      callback=self.on_connect)

            self.logger.info("Successfully connected to the robot")
        except Exception as e:
            self.logger.error("Error while connecting to the robot: {}".format(e))

    def disconnect_robot(self, data_dict=None):
        self.logger.info("TODO: Disconnect from robot.")

    def exit_gracefully(self, data_dict=None):
        try:
            if self.db_change_thread is not None:
                self.db_change_thread.stop_running()
                self.db_helper.update_one(self.db_helper.interaction_collection,
                                          data_key="isConnected",
                                          data_dict={"isConnected": False, "timestamp": time.time()})
                time.sleep(2)
                # self.db_change_thread.join(timeout=2.0)
                if self.db_change_thread is not None and self.db_change_thread.is_alive():
                    self.logger.info("DB Thread is still alive!")

        except Exception as e:
            self.logger.error("Error while stopping thread: {} | {}".format(self.db_change_thread, e))
        finally:
            self.db_change_thread = None

    @inlineCallbacks
    def on_connect(self, session, details=None):
        try:
            yield self.logger.debug("Received session: {}".format(session))
            self.robot_controller = RobotController(robot_name=self.robot_name)
            self.robot_controller.set_session(session=session)
            self.logger.info("Finished setting the session")
            self.robot_controller.observe_interaction_events(self.on_block_executed, self.on_user_answer)
            self.robot_controller.observe_engagement_events(observer=self.on_engaged)

            # update speech certainty
            self.on_speech_certainty(data_dict=self.db_helper.find_one(self.db_helper.interaction_collection,
                                                                       "speechCertainty"))
            self.logger.info("Session is successfully set")
            self.setup_db_stream()
        except Exception as e:
            yield self.logger.error("Error while setting the robot controller {}: {}".format(session, e))

    def setup_db_stream(self):
        try:
            self.db_helper.update_one(self.db_helper.robot_collection,
                                      data_key="isConnected",
                                      data_dict={"isConnected": True, "timestamp": time.time()})

            self.start_listening_to_db_stream()
            self.logger.info("Finished")
        except Exception as e:
            self.logger.error("Error while setting up db stream: {}".format(e))

    def on_user_answer(self, val=None):
        try:
            self.logger.debug("User Answer: {}".format(val))

            self.on_block_executed(val=True, execution_result="" if val is None else val)
        except Exception as e:
            self.logger.error("Error while storing user answer: {}".format(e))

    def on_block_executed(self, val=None, execution_result=""):
        try:
            self.db_helper.update_one(self.db_helper.robot_collection,
                                      data_key="isExecuted",
                                      data_dict={"isExecuted": {"value": True, "executionResult": execution_result},
                                                 "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while storing block completed: {}".format(e))

    def on_engaged(self, val=None):
        try:
            self.db_helper.update_one(self.db_helper.robot_collection,
                                      data_key="isEngaged",
                                      data_dict={"isEngaged": False if val is None else val, "timestamp": time.time()})
        except Exception as e:
            self.logger.error("Error while storing isEngaged: {}".format(e))

    def on_wakeup(self, data_dict=None):
        self.logger.info("Data received: {}".format(data_dict))
        self.robot_controller.posture(wakeup=True)

    def on_rest(self, data_dict=None):
        self.logger.info("Data received: {}".format(data_dict))
        self.robot_controller.posture(wakeup=False)

    def on_animate(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            animation_name = data_dict["animateRobot"]["animation"]
            message = data_dict["animateRobot"]["message"]
            if message is None or message == "":
                self.robot_controller.execute_animation(animation_name=animation_name)
            else:
                self.robot_controller.animated_say(message=message, animation_name=animation_name)
        except Exception as e:
            self.logger.error("Error while extracting animate data: {} | {}".format(data_dict, e))

    def on_hide_tablet_image(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.robot_controller.tablet_image(hide=data_dict["hideTabletImage"])
        except Exception as e:
            self.logger.error("Error while extracting tablet image: {} | {}".format(data_dict, e))

    def on_interaction_block(self, data_dict=None):
        try:
            self.logger.info("Received Interaction Block data.")
            block_dict = data_dict["interactionBlock"]
            interaction_block = InteractionBlock.create_interaction_block(block_dict)
            if interaction_block:
                interaction_block.id = block_dict["id"]
                interaction_block.is_hidden = True

                self.robot_controller.load_html_page(tablet_page=interaction_block.tablet_page)
                self.robot_controller.customized_say(interaction_block=interaction_block)
        except Exception as e:
            self.logger.error("Error while extracting interaction block: {} | {}".format(data_dict, e))

    def on_start_interaction(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.robot_controller.is_interacting = data_dict["startInteraction"]
            # self.robot_controller.reset()
        except Exception as e:
            self.logger.error("Error while extracting interaction data: {} | {}".format(data_dict, e))

    def on_start_engagement(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.robot_controller.engagement(start=data_dict["startEngagement"])
        except Exception as e:
            self.logger.error("Error while extracting engagement data: {} | {}".format(data_dict, e))

    def on_touch(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.robot_controller.touch()
        except Exception as e:
            self.logger.error("Error while extracting touch data: {} | {}".format(data_dict, e))

    def on_speech_certainty(self, data_dict=None):
        try:
            self.logger.info("Data received: {}".format(data_dict))
            self.robot_controller.update_speech_certainty(speech_certainty=data_dict["speechCertainty"])
        except Exception as e:
            self.logger.error("Error while extracting speech certainty data: {} | {}".format(data_dict, e))

    def start_listening_to_db_stream(self):
        if self.db_change_thread is None:
            self.db_change_thread = DBChangeStreamThread()

            self.db_change_thread.add_data_observers(
                observers_dict={
                    "connectRobot": self.connect_robot,
                    "disconnectRobot": self.disconnect_robot,
                    "wakeUpRobot": self.on_wakeup,
                    "restRobot": self.on_rest,
                    "animateRobot": self.on_animate,
                    "interactionBlock": self.on_interaction_block,
                    "startInteraction": self.on_start_interaction,
                    "startEngagement": self.on_start_engagement,
                    "hideTabletImage": self.on_hide_tablet_image,
                    "speechCertainty": self.on_speech_certainty
                }
            )

        self.db_change_thread.start_listening(self.db_helper.interaction_collection)
