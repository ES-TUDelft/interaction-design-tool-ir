#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========================= #
# UI_EDIT_BLOCK_CONTROLLER #
# ========================= #
# Class for controlling the block editor GUI.
#
# @author ES
# **

import logging

from PyQt5 import QtCore, QtWidgets

from block_manager.enums.block_enums import SocketType
from es_common.enums.command_enums import ActionCommand
from es_common.factory.command_factory import CommandFactory
from interaction_manager.utils import config_helper
import es_common.hre_config as pconfig
from es_common.model.interaction_block import InteractionBlock
from interaction_manager.model.speech_act import SpeechAct
from interaction_manager.view.ui_editblock_dialog import Ui_EditBlockDialog
from es_common.model.tablet_page import TabletPage
from es_common.model.topic_tag import TopicTag


class UIEditBlockController(QtWidgets.QDialog):
    def __init__(self, interaction_block, block_controller, music_controller=None, robot_controller=None, parent=None):
        super(UIEditBlockController, self).__init__(parent)

        self.logger = logging.getLogger("EditBlockController")

        self.block_controller = block_controller
        self.interaction_block = interaction_block
        self.music_controller = music_controller
        self.robot_controller = robot_controller

        self.pattern = self.interaction_block.pattern.lower()
        self.pattern_settings = config_helper.get_patterns()[self.pattern]

        # init UI elements
        self.ui = Ui_EditBlockDialog()
        self.ui.setupUi(self)

        # init ui elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        if self.interaction_block is None:
            self.interaction_block = InteractionBlock()

        self.connected_interaction_blocks = self.interaction_block.get_connected_interaction_blocks(
            socket_type=SocketType.OUTPUT
        )

        self.setWindowTitle("Edit Block")

        # block properties
        self.ui.patternLineEdit.setText(self.pattern)
        self.ui.blockDescriptionLineEdit.setText(self.interaction_block.description)

        # Message
        speech_act = self.interaction_block.speech_act
        self.ui.messageTextEdit.setText(speech_act.message)
        # self.ui.messageTypeComboBox.setCurrentIndex(
        #     self.ui.messageTypeComboBox.findText(speech_act.message_type.name.title(), QtCore.Qt.MatchFixedString))

        # Actions
        self.set_actions()

        # gestures
        self.ui.openGestureLineEdit.setText(
            "{}".format(self.interaction_block.behavioral_parameters.gesture.gestures['open']))
        self.ui.closeGestureLineEdit.setText(
            "{}".format(self.interaction_block.behavioral_parameters.gesture.gestures['close']))
        gestures = config_helper.get_gestures()
        self.ui.openGestureComboBox.clear()
        self.ui.openGestureComboBox.addItems([pconfig.SELECT_OPTION])
        self.ui.openGestureComboBox.addItems(sorted([g for g in gestures['open']]))
        self.ui.openGestureComboBox.currentIndexChanged.connect(lambda: self.update_gesture_text_box(
            combo_box=self.ui.openGestureComboBox,
            text_box=self.ui.openGestureLineEdit,
            gesture_type="open"
        ))
        self.ui.closeGesturesComboBox.clear()
        self.ui.closeGesturesComboBox.addItems([pconfig.SELECT_OPTION])
        self.ui.closeGesturesComboBox.addItems(sorted([g for g in gestures['close']]))
        self.ui.closeGesturesComboBox.currentIndexChanged.connect(lambda: self.update_gesture_text_box(
            combo_box=self.ui.closeGesturesComboBox,
            text_box=self.ui.closeGestureLineEdit,
            gesture_type="close"
        ))
        if self.robot_controller is not None:
            # Open Gestures
            self.ui.testOpenGesturesPushButton.setEnabled(True)
            self.ui.testOpenGesturesPushButton.clicked.connect(lambda: self.test_animation(
                animation_name=self.ui.openGestureLineEdit.text()))
            # Close Gestures
            self.ui.testCloseGesturePushButton.setEnabled(True)
            self.ui.testCloseGesturePushButton.clicked.connect(lambda: self.test_animation(
                animation_name=self.ui.closeGestureLineEdit.text()))

        # tablet page
        # self.ui.tabletPageNameComboBox.clear()
        # self.ui.tabletPageNameComboBox.addItems(pconfig.tablet_pages)
        tablet_page = self.interaction_block.tablet_page
        if not tablet_page.name == "":
            self.ui.tabletPageNameComboBox.setCurrentIndex(
                self.ui.tabletPageNameComboBox.findText(tablet_page.name, QtCore.Qt.MatchFixedString))
        self.ui.tabletImageComboBox.clear()
        self.ui.tabletImageComboBox.addItems(config_helper.get_tablet_properties()["images"])
        if not tablet_page.image == "":
            self.ui.tabletImageComboBox.setCurrentIndex(
                self.ui.tabletImageComboBox.findText(tablet_page.image, QtCore.Qt.MatchFixedString))
        self.ui.tabletHeadingTextEdit.setText(tablet_page.heading)
        self.ui.tabletInfoTextEdit.setText(tablet_page.text)

        # topic tag
        self.ui.topicNameComboBox.currentIndexChanged.connect(self.update_tags)
        self.ui.topicTagComboBox.currentIndexChanged.connect(self.update_pages)
        self.toggle_topic_tab()

    def toggle_topic_tab(self):
        topic_index = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QtWidgets.QWidget, 'topicTab'))

        if self.pattern_settings["topic"] == "":
            self.ui.tabWidget.setTabEnabled(topic_index, False)  # self.ui.topicTab.setEnabled(False)
            self._set_topic_tab(reset=True)
            self.ui.tabWidget.removeTab(topic_index)
        else:
            self.ui.topicTab.setEnabled(True)
            self._set_topic_tab(reset=False)

    def set_actions(self):
        # TODO: Use the action property defined in the pattern

        if "action" in self.pattern:
            try:
                actions = [a for a in ActionCommand.keys()]
                self.toggle_action_tab(enable=True)

                self.ui.actionComboBox.addItems([pconfig.SELECT_OPTION])
                self.ui.actionComboBox.addItems(actions)

                # listeners
                self.ui.actionComboBox.currentIndexChanged.connect(self.on_action_change)
                # music
                self.ui.playlistComboBox.currentIndexChanged.connect(self.update_tracks_combo)
                self.ui.animationsCheckBox.stateChanged.connect(lambda: self.ui.animationsComboBox.setEnabled(
                    self.ui.animationsCheckBox.isChecked()))
                self.ui.animationsComboBox.addItems([a for a in config_helper.get_animations()])

                # if we're changing the min range and the value > max ==> update max with min value
                self.ui.rangeMinSpinBox.valueChanged.connect(lambda: self.verify_range(update_max=True))
                # if we're changing the max range and the value < min ==> update min with max value
                self.ui.rangeMaxSpinBox.valueChanged.connect(lambda: self.verify_range(update_max=False))

                # check if the block contains an action
                if self.interaction_block.action_command is not None:
                    comm_type = self.interaction_block.action_command.command_type
                    # update action name
                    self.ui.actionComboBox.setCurrentIndex(
                        self.ui.actionComboBox.findText(comm_type.name, QtCore.Qt.MatchFixedString))
                    # update range
                    # if comm_type is ActionCommand.DRAW_NUMBER:
                    #     self.ui.rangeMinSpinBox.setValue(self.interaction_block.action_command.range_min)
                    #     self.ui.rangeMaxSpinBox.setValue(self.interaction_block.action_command.range_max)
                    if comm_type is ActionCommand.WAIT:
                        self.ui.timeSpinBox.setValue(self.interaction_block.action_command.wait_time)
                    elif comm_type is ActionCommand.PLAY_MUSIC:
                        self.ui.playlistComboBox.setCurrentIndex(
                            self.ui.playlistComboBox.findText(self.interaction_block.action_command.playlist,
                                                              QtCore.Qt.MatchFixedString))
                        self.ui.tracksComboBox.setCurrentIndex(
                            self.ui.tracksComboBox.findText(self.interaction_block.action_command.track,
                                                            QtCore.Qt.MatchFixedString))
                        self.ui.playTimeSpinBox.setValue(self.interaction_block.action_command.play_time)

                        anim = self.interaction_block.action_command.animations_key
                        if anim is not None and anim != "":
                            self.ui.animationsCheckBox.setChecked(True)
                            self.ui.animationsComboBox.setCurrentIndex(
                                self.ui.animationsComboBox.findText(anim,
                                                                    QtCore.Qt.MatchFixedString))
            except Exception as e:
                self.logger.error("Error while setting actions! {}".format(e))

        else:  # otherwise: hide the actions
            self.toggle_action_tab(enable=False)

    def toggle_action_tab(self, enable=False):
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QtWidgets.QWidget, 'actionTab'))
        self.ui.tabWidget.setTabEnabled(tab_index, enable)
        self.ui.rangeGroupBox.setHidden(True)
        self.ui.musicGroupBox.setHidden(True)
        self.ui.timeGroupBox.setHidden(True)

        if enable is False:
            self.ui.actionComboBox.setHidden(True)
            self.ui.tabWidget.removeTab(tab_index)

    def on_action_change(self):
        hide_range, hide_music, hide_time = True, True, True
        # if self.ui.actionComboBox.currentText() in ActionCommand.DRAW_NUMBER.name:
        #     hide_range = False
        if self.ui.actionComboBox.currentText() in ActionCommand.WAIT.name:
            hide_time = False
        elif self.ui.actionComboBox.currentText() in ActionCommand.PLAY_MUSIC.name:
            hide_music = False
            self.update_playlist_combo()

        self.ui.rangeGroupBox.setHidden(hide_range)
        self.ui.timeGroupBox.setHidden(hide_time)
        self.ui.musicGroupBox.setHidden(hide_music)

    def verify_range(self, update_max):
        if self.ui.rangeMinSpinBox.value() >= self.ui.rangeMaxSpinBox.value():
            # set the max val to min+1 if update_max is True; else set the min val to max-1
            self.ui.rangeMaxSpinBox.setValue(self.ui.rangeMinSpinBox.value() + 1) if update_max is True \
                else self.ui.rangeMinSpinBox.setValue(self.ui.rangeMaxSpinBox.value() - 1)

    def update_playlist_combo(self):
        self.ui.playlistComboBox.clear()
        if self.music_controller is None:
            return

        try:
            if self.music_controller.playlists is None or len(self.music_controller.playlists) == 0:
                return
            self.ui.playlistComboBox.addItems([pconfig.SELECT_OPTION])
            self.ui.playlistComboBox.addItems([p for p in self.music_controller.playlists.keys()])
        except Exception as e:
            self.logger.error("Error while loading the playlists! {}".format(e))

    def update_tracks_combo(self):
        self.ui.tracksComboBox.clear()
        if self.music_controller is None:
            return
        playlist = self.ui.playlistComboBox.currentText()
        try:
            if playlist != pconfig.SELECT_OPTION:
                self.ui.tracksComboBox.addItems([pconfig.SELECT_OPTION])
                self.ui.tracksComboBox.addItems([t for t in self.music_controller.playlists[playlist]["tracks"]])
        except Exception as e:
            self.logger.error("Error while loading tracks for playlist: {}! {}".format(playlist, e))

    def update_tags(self):
        # tags
        self.ui.topicTagComboBox.clear()
        # self.ui.topicTagComboBox.addItems([pconfig.SELECT_OPTION])

        tags = self.pattern_settings["tags"]
        if len(tags) > 1:
            self.ui.topicTagComboBox.addItems([pconfig.SELECT_OPTION])
        self.ui.topicTagComboBox.addItems(tags)

        tag = self.interaction_block.topic_tag.name
        if tag != "" and tag.lower() in tags:
            self.ui.topicTagComboBox.setCurrentIndex(
                self.ui.topicTagComboBox.findText(tag.lower(), QtCore.Qt.MatchFixedString))

        self.update_pages()

    def update_pages(self):
        self.ui.tabletPageNameComboBox.clear()
        self.ui.tabletPageNameComboBox.addItems([pconfig.SELECT_OPTION])

        # No topic ==> use default pages
        # Topic with no tag ==> use default
        # Topic with tag ==> check options
        if self.pattern_settings["topic"] == "":
            self.ui.tabletPageNameComboBox.addItems(self.pattern_settings["tablet"])
        else:
            # check topic tag pages
            tag = "{}".format(self.ui.topicTagComboBox.currentText())
            tags = config_helper.get_tags()

            if (pconfig.SELECT_OPTION in tag) or (tag == "") or tag not in tags:
                # use default pages
                self.ui.tabletPageNameComboBox.addItems(self.pattern_settings["tablet"])
            else:
                self.ui.tabletPageNameComboBox.addItems(tags[tag]["pages"])

        tablet_page = self.interaction_block.tablet_page
        if not tablet_page.name == "":
            self.ui.tabletPageNameComboBox.setCurrentIndex(
                self.ui.tabletPageNameComboBox.findText(tablet_page.name, QtCore.Qt.MatchFixedString))

    def update_gesture_text_box(self, combo_box, text_box, gesture_type):
        gesture_name = "{}".format(combo_box.currentText())

        if pconfig.SELECT_OPTION in gesture_name:
            return

        gest = config_helper.get_gestures()[gesture_type]
        if gesture_name in gest:
            text_box.setText("{}".format(gest[gesture_name]))

    def test_animation(self, animation_name=None):
        if self.robot_controller is None or animation_name is None or animation_name.strip() == "":
            return
        try:
            self.robot_controller.execute_animation(animation_name=animation_name)
        except Exception as e:
            self.logger.error("Error while testing animation: {}! {}".format(animation_name, e))

    def _set_topic_tab(self, reset=False):
        # clear the combo-boxes
        self.ui.topicNameComboBox.clear()
        self.ui.topicTagComboBox.clear()

        # set answers and feedbacks
        if reset is True:
            tag, topic, a1, a2, = ("",) * 4
        else:
            topic_tag = self.interaction_block.topic_tag
            tag = topic_tag.name
            topic = topic_tag.topic

            a1 = '' if len(topic_tag.answers) == 0 else topic_tag.answers[0]
            a2 = '' if len(topic_tag.answers) < 2 else topic_tag.answers[1]

            # topic properties ==> we're using one topic for now!
            # self.ui.topicNameComboBox.addItems([pconfig.SELECT_OPTION])
            # available_topics = [t for t in config_helper.get_topics()]
            self.ui.topicNameComboBox.addItems([self.pattern_settings["topic"]])

            if topic.lower() != "" and topic.lower() != self.pattern_settings["topic"]:
                self.ui.topicNameComboBox.addItems([topic.lower()])
                self.ui.topicNameComboBox.setCurrentIndex(
                    self.ui.topicNameComboBox.findText(topic.lower(), QtCore.Qt.MatchFixedString))
            # tags
            self.update_tags()

        # update the slots
        self.ui.answer1TextEdit.setText(a1)
        self.ui.answer2TextEdit.setText(a2)

        self.update_go_to()

    def update_go_to(self):
        if self.connected_interaction_blocks is not None and len(self.connected_interaction_blocks) > 0:
            items = [pconfig.SELECT_OPTION]
            items.extend(["{}: {}".format(b.title, b.description) for b in self.connected_interaction_blocks])

            self.ui.answer1GoToComboBox.addItems(items)
            self.ui.answer2GoToComboBox.addItems(items)

            goto_ids = self.interaction_block.topic_tag.goto_ids
            if goto_ids is None or len(goto_ids) == 0:
                return

            for i in range(len(goto_ids)):
                b = self.block_controller.get_block_by_parent_id(parent_id=goto_ids[i])
                if b is None:  # block is not found!
                    self.logger.debug("Found 0 blocks for id: {}".format(goto_ids[i]))
                    continue

                opt = "{}: {}".format(b.title, b.description)
                if opt in items:
                    if i == 0:
                        self.ui.answer1GoToComboBox.setCurrentIndex(
                            self.ui.answer1GoToComboBox.findText(opt, QtCore.Qt.MatchFixedString))
                    else:
                        self.ui.answer2GoToComboBox.setCurrentIndex(
                            self.ui.answer2GoToComboBox.findText(opt, QtCore.Qt.MatchFixedString))

    def get_speech_act(self):
        return SpeechAct.create_speech_act({"message": "{}".format(self.ui.messageTextEdit.toPlainText()).strip(),
                                            "message_type": "Informal"})
        # .format(self.ui.messageTypeComboBox.currentText())

    def get_topic_tag(self):
        topic_tag = TopicTag()
        if self.ui.topicTab.isEnabled():
            topic_tag.name = "{}".format(self.ui.topicTagComboBox.currentText())
            topic_tag.topic = "{}".format(self.ui.topicNameComboBox.currentText())
            topic_tag.answers = ["{}".format(self.ui.answer1TextEdit.toPlainText()).strip(),
                                 "{}".format(self.ui.answer2TextEdit.toPlainText()).strip()]

            # set GoTos
            goto_ids = [-1, -1]
            options = ["{}".format(self.ui.answer1GoToComboBox.currentText()),
                       "{}".format(self.ui.answer2GoToComboBox.currentText())]
            for i in range(len(options)):
                if self._is_valid_option(options[i]):
                    b = self._get_block_from_details(*options[i].split(":"))
                    if b is not None:
                        goto_ids[i] = b.id
            self.logger.debug("GoTo IDS: {} | {}".format(*goto_ids))
            topic_tag.goto_ids = goto_ids

        return topic_tag

    def get_tablet_page(self):
        return TabletPage(name="{}".format(self.ui.tabletPageNameComboBox.currentText()),
                          heading="{}".format(self.ui.tabletHeadingTextEdit.toPlainText()).strip(),
                          text="{}".format(self.ui.tabletInfoTextEdit.toPlainText()).strip(),
                          image="{}".format(self.ui.tabletImageComboBox.currentText()),
                          )

    def get_command(self):
        if self.ui.actionComboBox.isHidden():
            return None

        comm_name = "{}".format(self.ui.actionComboBox.currentText())
        if comm_name in ActionCommand.keys():
            args = self.get_command_arguments(comm_name=comm_name)
            if args is None:
                if comm_name == ActionCommand.PLAY_MUSIC.name:
                    return None
                return CommandFactory.create_command(ActionCommand[comm_name])
            else:
                return CommandFactory.create_command(ActionCommand[comm_name], *args)

        return None

    def get_command_arguments(self, comm_name):
        args = None
        # if comm_name == ActionCommand.DRAW_NUMBER.name:
        #     args = [self.ui.rangeMinSpinBox.value(), self.ui.rangeMaxSpinBox.value()]
        if comm_name == ActionCommand.WAIT.name:
            args = [self.ui.timeSpinBox.value()]
        elif comm_name == ActionCommand.PLAY_MUSIC.name:
            args = self.get_music_arguments()

        return args

    def get_music_arguments(self):
        args = []
        try:
            playlist = self.ui.playlistComboBox.currentText()
            track = self.ui.tracksComboBox.currentText()

            if playlist == "" or playlist in pconfig.SELECT_OPTION \
                    or track == "" or track in pconfig.SELECT_OPTION:
                args = None
            else:
                args = [playlist, track, int(self.ui.playTimeSpinBox.value())]
                if self.ui.animationsCheckBox.isChecked():
                    args.append("{}".format(self.ui.animationsComboBox.currentText()))
        except Exception as e:
            self.logger.error("Error while loading music arguments! {}".format(e))
        finally:
            self.logger.debug("*** ARGS: {}".format(args))
            return args

    def get_interaction_block(self):
        d_block = self.interaction_block.clone()
        d_block.name = "{}".format(self.ui.patternLineEdit.text().strip())
        d_block.description = "{}".format(self.ui.blockDescriptionLineEdit.text().strip())
        d_block.speech_act = self.get_speech_act()
        d_block.topic_tag = self.get_topic_tag()
        d_block.tablet_page = self.get_tablet_page()
        d_block.action_command = self.get_command()
        # gestures
        d_block.behavioral_parameters.gesture.set_gestures(open_gesture="{}".format(self.ui.openGestureLineEdit.text()),
                                                           close_gesture="{}".format(
                                                               self.ui.closeGestureLineEdit.text()))

    def update_interaction_block(self, int_block):
        if int_block is None:
            return

        int_block.name = "{}".format(self.ui.patternLineEdit.text().strip())
        int_block.description = "{}".format(self.ui.blockDescriptionLineEdit.text().strip())
        int_block.speech_act = self.get_speech_act()
        int_block.topic_tag = self.get_topic_tag()
        int_block.tablet_page = self.get_tablet_page()

        # don't update music command if there is no connection to the music service
        if "{}".format(self.ui.actionComboBox.currentText()) == ActionCommand.PLAY_MUSIC.name:
            if self.music_controller is not None:
                int_block.action_command = self.get_command()
        else:
            int_block.action_command = self.get_command()
        # gestures
        int_block.set_gestures(open_gesture="{}".format(self.ui.openGestureLineEdit.text()),
                               close_gesture="{}".format(self.ui.closeGestureLineEdit.text()))

    def _is_valid_option(self, option):
        if option is not None and option != "" and option != pconfig.SELECT_OPTION:
            return True

        return False

    def _get_block_from_details(self, title, desc):
        for b in self.connected_interaction_blocks:
            if b.title == title.strip() and b.description == desc.strip():
                return b
        return None

    def _toggle_item(self, item, status):
        if item is None or status is None:
            return
        try:
            item.setEnabled(status)
            self.repaint()
        except Exception as e:
            self.logger.info("Error while enabling item: {} | {}".format(item, e))
        finally:
            return
