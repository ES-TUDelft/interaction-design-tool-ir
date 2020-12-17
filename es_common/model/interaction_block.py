#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# Interaction_BLOCK #
# ================= #
# Model for the interaction blocks.
#
# @author ES
# **
import logging
from collections import OrderedDict

from block_manager.enums.block_enums import SocketType, ExecutionMode
from es_common.datasource.serializable import Serializable
from es_common.enums.command_enums import ActionCommand
from es_common.factory.command_factory import CommandFactory
from es_common.model.design_module import DesignModule
from es_common.model.tablet_page import TabletPage
from es_common.model.topic_tag import TopicTag
from es_common.utils.data_helper import join_array
from es_common.model.speech_act import SpeechAct


class InteractionBlock(Serializable):
    def __init__(self, name=None, pattern=None, block=None):
        super(InteractionBlock, self).__init__()

        self.logger = logging.getLogger("Interaction Block")

        self.name = "Start" if name is None else name
        self.pattern = pattern if pattern is not None else self.name
        self.topic_tag = TopicTag()
        self.tablet_page = TabletPage()

        self.icon_path = None

        self.speech_act = SpeechAct()
        self.animation = None
        self.block = block

        # action command
        self.action_command = None  # ESCommand()
        self.interaction_module_name = None
        self.design_module = None

        self.execution_mode = ExecutionMode.NEW  # by default

        self.interaction_start_time = 0
        self.interaction_end_time = 0
        self.is_hidden = False
        self.execution_result = ""

    def clone(self):
        return InteractionBlock.create_interaction_block(self.to_dict)

    def set_icon_path(self, icon_path):
        # TODO: use config file to retrieve the path
        if icon_path is None:
            self.icon_path = ":/hreresources/pepper-icons/pepper-standing.png"
        elif 'hreresources' in icon_path:
            self.icon_path = icon_path
        else:
            self.icon_path = ":/hreresources/pepper-icons/{}".format(icon_path)

    def get_connected_blocks(self, socket_type=SocketType.OUTPUT):
        return self.block.get_connected_blocks(socket_type=socket_type)

    def get_connected_interaction_blocks(self, socket_type=SocketType.OUTPUT):
        connected_b = []
        try:
            blocks = self.get_connected_blocks(socket_type)
            if blocks is not None:
                connected_b = [b.parent for b in blocks]
        except Exception as e:
            self.logger.error("Error while checking for connected interaction blocks! {}".format(e))
        finally:
            return connected_b

    def is_valid_user_input(self, user_input):
        """
        For the simulator
        :param user_input: input to verify
        :return: True  if the input is in the list of valid answers; False otherwise.
        """
        if user_input is None:
            return False

        # check the answers
        for i in range(len(self.topic_tag.answers)):
            # if the result is in the answers
            if user_input.lower() in self.topic_tag.answers[i].lower():
                return True
        return False

    def get_next_interaction_block(self, execution_result=None):
        next_int_block = None
        connecting_edge = None

        int_blocks = self.get_connected_interaction_blocks(socket_type=SocketType.OUTPUT)

        if int_blocks is None or len(int_blocks) == 0:  # no next block available!
            return next_int_block, connecting_edge

        # TODO: verify the returned user input from Pepper
        try:
            # in the absence of a condition
            if execution_result is None or execution_result == "" or len(self.topic_tag.answers) == 0:
                # select first if possible
                self.execution_result = ""
                next_int_block = int_blocks[0]  # we already verified the len to be > 0
            else:
                # check the answers
                for i in range(len(self.topic_tag.answers)):
                    # if the result is in the answers ==> go to appropriate interaction block
                    ans = join_array([self.topic_tag.answers[i]])
                    ans = [s.strip().lower() for s in ans]
                    if execution_result.strip().lower() in ans:
                        next_int_block = self._get_block_by_id(int_blocks, self.topic_tag.goto_ids[i])
                        break
            # if next_int_block:
            #     next_int_block.execution_result = execution_result
            connecting_edge = self.get_output_connected_edge(next_int_block)
            self.logger.debug("Next block is: {} | {}".format(0 if next_int_block is None else next_int_block.title,
                                                              next_int_block.message))
            return next_int_block, connecting_edge
        except Exception as e:
            self.logger.error("Error while attempting to get the next block! {}".format(e))
            return next_int_block, connecting_edge

    def set_selected(self, val):
        if val is not None and self.block:
            self.block.set_selected(val)

    def _get_block_by_id(self, b_lst, target_id):
        for b in b_lst:
            if b.id == target_id:
                return b
        return None

    def get_output_connected_edge(self, other_interaction_block):
        if other_interaction_block is None:
            return None

        for edge in self.block.get_edges(socket_type=SocketType.OUTPUT):
            if edge.start_socket in (self.block.outputs + other_interaction_block.block.inputs) \
                    and edge.end_socket in (self.block.outputs + other_interaction_block.block.inputs):
                return edge
        return None

    def has_action(self, action_type):
        return self.action_command is not None and self.action_command.command_type is action_type

    def has_interaction_module(self, module_name):
        return self.interaction_module_name == module_name

    def get_combined_answers(self):
        return self.topic_tag.get_combined_answers()

    # ===========
    # PROPERTIES
    # ===========
    @property
    def icon(self):
        return self.icon_path.replace(":/hreresources/pepper-icons/", "")

    @property
    def speech_act(self):
        return self.__speech_act

    @speech_act.setter
    def speech_act(self, speech_act):
        self.__speech_act = speech_act.clone() if speech_act is not None else SpeechAct()

    @property
    def message(self):
        # if there is an action, execute it to adapt the message, if needed
        # uses the speech_act property above to return the message
        if self.action_command is None or self.action_command.is_speech_related is False:
            return self.speech_act.message

        # the action has an effect on the speech act
        # append the execution result to the message
        return "{}: {}".format(self.speech_act.message, self.action_command.execute())

    @message.setter
    def message(self, value):
        self.speech_act.message = value

    @property
    def answers(self):
        return self.topic_tag.answers if self.topic_tag else None

    @answers.setter
    def answers(self, val):
        self.topic_tag.answers = val

    @property
    def goto_ids(self):
        return self.topic_tag.goto_ids if self.topic_tag else None

    @goto_ids.setter
    def goto_ids(self, val):
        self.topic_tag.goto_ids = val

    @property
    def description(self):
        return "" if self.block is None else self.block.description

    @description.setter
    def description(self, desc):
        if self.block is not None:
            self.block.description = desc

    @property
    def title(self):
        return "" if self.block is None else self.block.title

    @property
    def to_dict(self):
        block_dict = OrderedDict([
            ("id", self.id),
            ("name", self.name),
            ("pattern", self.pattern),
            ("description", self.description),
            ("topic_tag", self.topic_tag.to_dict),
            ("tablet_page", self.tablet_page.to_dict),
            ("icon_path", self.icon_path),
            ("speech_act", self.speech_act.to_dict),
            ("animation", self.animation),
            ("execution_result", self.execution_result),
            ("action_command", self.action_command.serialize() if self.action_command is not None else {}),
            ("interaction_module_name", self.interaction_module_name),
            ('design_module', {} if self.design_module is None else self.design_module.to_dict),
            ("block", self.block.id if self.block is not None else 0),
            ("is_hidden", self.is_hidden),
            ("interaction_start_time", self.interaction_start_time),
            ("interaction_end_time", self.interaction_end_time),
        ])

        return block_dict

    @staticmethod
    def create_interaction_block(block_dict):
        if block_dict:
            b_pattern = block_dict["pattern"] if "pattern" in block_dict.keys() else block_dict["name"]
            int_block = InteractionBlock(name=block_dict['name'],
                                         pattern=b_pattern)
            int_block.topic_tag = TopicTag.create_topic_tag(tag_dict=block_dict['topic_tag'])
            int_block.tablet_page = TabletPage.create_tablet_page(page_dict=block_dict["tablet_page"])
            int_block.icon_path = block_dict['icon_path']

            if 'behavioral_parameters' in block_dict.keys():  # otherwise, keep default values
                int_block.speech_act = SpeechAct.create_speech_act(block_dict['behavioral_parameters'])
            if "speech_act" in block_dict.keys():
                int_block.speech_act = SpeechAct.create_speech_act(block_dict["speech_act"])

            int_block.animation = block_dict["animation"] if "animation" in block_dict.keys() else None
            int_block.is_hidden = block_dict["is_hidden"] if "is_hidden" in block_dict.keys() else False

            if "interaction_module_name" in block_dict.keys():
                int_block.interaction_module_name = block_dict["interaction_module_name"]

            if "design_module" in block_dict.keys():
                int_block.design_module = DesignModule.create_design_module(block_dict["design_module"])

            if "execution_result" in block_dict.keys():
                int_block.execution_result = block_dict["execution_result"]

            # if any('interaction' in k for k in block_dict.keys()):
            int_block.interaction_start_time = block_dict['interaction_start_time']
            int_block.interaction_end_time = block_dict['interaction_end_time']

            return int_block

        return None

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return self.to_dict

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        self.block = hashmap[data["block"]]

        if "action_command" in data.keys():
            action_data = data["action_command"]
            if len(action_data) > 0:
                self.action_command = CommandFactory.create_command(ActionCommand[action_data["command_type"]])
                self.action_command.deserialize(action_data, hashmap)

        return True
