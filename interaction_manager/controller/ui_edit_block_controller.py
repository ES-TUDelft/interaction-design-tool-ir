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
import os

from block_manager.enums.block_enums import SocketType
from es_common.enums.command_enums import ActionCommand
from es_common.enums.module_enums import InteractionModule
from es_common.factory.command_factory import CommandFactory
from es_common.model.design_module import DesignModule
from es_common.model.interaction_block import InteractionBlock
from es_common.model.tablet_page import TabletPage
from es_common.model.topic_tag import TopicTag
from es_common.utils.qt import QtCore, QtWidgets, qtSlot
from es_common.model.speech_act import SpeechAct
from interaction_manager.utils import config_helper
from interaction_manager.view.ui_editblock_dialog import Ui_EditBlockDialog

SELECT_OPTION = "-- SELECT --"


class UIEditBlockController(QtWidgets.QDialog):
    def __init__(self, interaction_block, block_controller, music_controller=None, robot_controller=None, parent=None):
        super(UIEditBlockController, self).__init__(parent)

        self.logger = logging.getLogger("EditBlockController")

        self.block_controller = block_controller
        self.interaction_block = interaction_block
        self.music_controller = music_controller
        self.robot_controller = robot_controller

        self.pattern_settings, self.pattern = self._get_pattern_settings(self.interaction_block.pattern.lower())

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

        # Animation
        self.ui.animationLineEdit.setText(self.interaction_block.animation)
        self.ui.animationsComboBox.currentIndexChanged.connect(self.on_animation_change)

        # Actions
        self.set_actions()

        # Modules
        self.set_modules()

        # Gestures tab: remove!
        beh_tab_index = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QtWidgets.QWidget, "behaviorsTab"))
        self.ui.tabWidget.removeTab(beh_tab_index)

        # tablet page
        self.set_tablet_tab()

        # topic tag
        self.toggle_topic_tab()

    def _get_pattern_settings(self, pattern_name):
        patterns = config_helper.get_patterns()
        pattern_settings = {}
        for p in patterns.keys():
            if pattern_name in p:
                self.logger.info("Pattern found: {}".format(p))
                return patterns[p], p
        return {}, ""

    def toggle_topic_tab(self):
        topic_index = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QtWidgets.QWidget, 'topicTab'))

        if self.pattern_settings["topic"] == "":
            self.ui.tabWidget.setTabEnabled(topic_index, False)  # self.ui.topicTab.setEnabled(False)
            self._set_topic_tab(reset=True)
            self.ui.tabWidget.removeTab(topic_index)
        else:
            self.ui.topicTab.setEnabled(True)
            self._set_topic_tab(reset=False)

    def set_modules(self):
        if "module" in self.pattern_settings.keys():
            try:
                self.toggle_module_tab(enable=True)

                # button listeners
                self.ui.moduleFileRadioButton.clicked.connect(lambda: self.enable_module_selection(enable_file=True))
                self.ui.moduleRandomizeRadioButton.clicked.connect(lambda: self.enable_module_selection(False))
                self.ui.moduleSelectFileToolButton.clicked.connect(self.select_file)
                self.ui.moduleSelectFolderToolButton.clicked.connect(self.select_folder)

                # TODO: check if needed
                modules = [m for m in InteractionModule.keys()]

                self.ui.moduleNameComboBox.addItems([SELECT_OPTION])
                self.ui.moduleNameComboBox.addItems(modules)

                # check if the block contains a module
                design_module = self.interaction_block.design_module
                if design_module:
                    if design_module.randomize:
                        self.ui.moduleRandomizeRadioButton.setChecked(True)
                        self.enable_module_selection(enable_file=False)
                        self.ui.moduleFolderNameLineEdit.setText(design_module.folder_name)
                    else:
                        self.ui.moduleFileNameLineEdit.setText(design_module.filename)

                    if design_module.name:
                        # update combobox current item
                        self.ui.moduleNameComboBox.setCurrentIndex(
                            self.ui.moduleNameComboBox.findText(design_module.name, QtCore.Qt.MatchFixedString))

                self.logger.info("Module tab is setup")
            except Exception as e:
                self.logger.error("Error while enabling the modules: {}".format(e))
        else:
            self.toggle_module_tab(enable=False)

    def toggle_module_tab(self, enable=False):
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QtWidgets.QWidget, 'moduleTab'))
        self.ui.tabWidget.setTabEnabled(tab_index, enable)

        if enable is False:
            self.ui.tabWidget.removeTab(tab_index)

    def enable_module_selection(self, enable_file=False):
        self.ui.moduleFileNameLineEdit.setEnabled(enable_file)
        self.ui.moduleSelectFileToolButton.setEnabled(enable_file)

        self.ui.moduleFolderNameLineEdit.setEnabled(not enable_file)
        self.ui.moduleSelectFolderToolButton.setEnabled(not enable_file)

    def select_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select JSON file", "", "JSON Files (*.json)",
                                                             options=options)
        self.ui.moduleFileNameLineEdit.setText(file_path)

    def select_folder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select a folder",
            os.getcwd(),
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        self.ui.moduleFolderNameLineEdit.setText(folder_name)

    def set_actions(self):
        # TODO: Use the action property defined in the pattern

        if "action" in self.pattern:
            try:
                actions = [a for a in ActionCommand.keys()]
                self.toggle_action_tab(enable=True)

                self.ui.actionComboBox.addItems([SELECT_OPTION])
                self.ui.actionComboBox.addItems(actions)

                # listeners
                self.ui.actionComboBox.currentIndexChanged.connect(self.on_action_change)
                # music
                self.ui.playlistComboBox.currentIndexChanged.connect(self.update_tracks_combo)
                self.ui.animationsCheckBox.stateChanged.connect(lambda: self.ui.animationsComboBox.setEnabled(
                    self.ui.animationsCheckBox.isChecked()))
                self.ui.animationsComboBox.addItems([a for a in config_helper.get_animations()])

                # check if the block contains an action
                if self.interaction_block.action_command is not None:
                    comm_type = self.interaction_block.action_command.command_type
                    # update action name
                    self.ui.actionComboBox.setCurrentIndex(
                        self.ui.actionComboBox.findText(comm_type.name, QtCore.Qt.MatchFixedString))
                    # update range
                    if comm_type is ActionCommand.CHECK_RESERVATIONS:
                        # TODO
                        self.logger.info("TODO")
                    elif comm_type is ActionCommand.WAIT:
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

        self.ui.musicGroupBox.setHidden(True)
        self.ui.timeGroupBox.setHidden(True)

        if enable is False:
            self.ui.actionComboBox.setHidden(True)
            self.ui.tabWidget.removeTab(tab_index)

    def on_action_change(self):
        hide_reservations, hide_music, hide_time = True, True, True
        if self.ui.actionComboBox.currentText() in ActionCommand.CHECK_RESERVATIONS.name:
            hide_reservations = False
        elif self.ui.actionComboBox.currentText() in ActionCommand.WAIT.name:
            hide_time = False
        elif self.ui.actionComboBox.currentText() in ActionCommand.PLAY_MUSIC.name:
            hide_music = False
            self.update_playlist_combo()

        self.ui.timeGroupBox.setHidden(hide_time)
        self.ui.musicGroupBox.setHidden(hide_music)

    def update_playlist_combo(self):
        self.ui.playlistComboBox.clear()
        if self.music_controller is None:
            return

        try:
            if self.music_controller.playlists is None or len(self.music_controller.playlists) == 0:
                return
            self.ui.playlistComboBox.addItems([SELECT_OPTION])
            self.ui.playlistComboBox.addItems([p for p in self.music_controller.playlists.keys()])
        except Exception as e:
            self.logger.error("Error while loading the playlists! {}".format(e))

    def update_tracks_combo(self):
        self.ui.tracksComboBox.clear()
        if self.music_controller is None:
            return
        playlist = self.ui.playlistComboBox.currentText()
        try:
            if playlist != SELECT_OPTION:
                self.ui.tracksComboBox.addItems([SELECT_OPTION])
                self.ui.tracksComboBox.addItems([t for t in self.music_controller.playlists[playlist]["tracks"]])
        except Exception as e:
            self.logger.error("Error while loading tracks for playlist: {}! {}".format(playlist, e))

    def set_tablet_tab(self):
        pages = config_helper.get_tablet_properties()["pages"].keys()
        tablet_page = self.interaction_block.tablet_page

        self.ui.tabletPageNameComboBox.clear()

        if "input" in self.pattern.lower():
            self.ui.tabletPageNameComboBox.addItems(config_helper.get_tablet_properties()["input_page"].keys())
        else:
            self.ui.tabletPageNameComboBox.addItems([SELECT_OPTION])
            self.ui.tabletPageNameComboBox.addItems(pages)
            if not tablet_page.name == "":
                self.ui.tabletPageNameComboBox.setCurrentIndex(
                    self.ui.tabletPageNameComboBox.findText(tablet_page.name, QtCore.Qt.MatchFixedString))

        self.ui.tabletImageComboBox.clear()
        self.ui.tabletImageComboBox.addItems(os.listdir(config_helper.get_tablet_properties()["pics_folder"]))
        if not tablet_page.image == "":
            self.ui.tabletImageComboBox.setCurrentIndex(
                self.ui.tabletImageComboBox.findText(tablet_page.image, QtCore.Qt.MatchFixedString))

        self.ui.tabletHeadingTextEdit.setText(tablet_page.heading)
        self.ui.tabletInfoTextEdit.setText(tablet_page.text)

    def _set_topic_tab(self, reset=False):
        # set answers and feedbacks
        if reset is True:
            tag, topic, a1, a2, = ("",) * 4
        else:
            topic_tag = self.interaction_block.topic_tag

            a1 = '' if len(topic_tag.answers) == 0 else topic_tag.answers[0]
            a2 = '' if len(topic_tag.answers) < 2 else topic_tag.answers[1]

        # update the slots
        self.ui.answer1TextEdit.setText(a1)
        self.ui.answer2TextEdit.setText(a2)

        self.update_go_to(self.interaction_block.topic_tag.goto_ids,
                          self.ui.answer1GoToComboBox, self.ui.answer2GoToComboBox)

    def update_go_to(self, goto_ids, combo_box_1, combo_box_2):
        if self.connected_interaction_blocks is not None and len(self.connected_interaction_blocks) > 0:
            items = [SELECT_OPTION]
            items.extend(["{}: {}".format(b.title, b.description) for b in self.connected_interaction_blocks])

            combo_box_1.addItems(items)
            combo_box_2.addItems(items)

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
                        combo_box_1.setCurrentIndex(
                            combo_box_1.findText(opt, QtCore.Qt.MatchFixedString))
                    else:
                        combo_box_2.setCurrentIndex(
                            combo_box_2.findText(opt, QtCore.Qt.MatchFixedString))

    def get_speech_act(self):
        return SpeechAct.create_speech_act({"message": "{}".format(self.ui.messageTextEdit.toPlainText()).strip(),
                                            "message_type": "Informal"})

    @qtSlot()
    def on_animation_change(self):
        animation = self.ui.animationsComboBox.currentText()
        if animation != SELECT_OPTION:
            self.ui.animationLineEdit.setText(animation)

    def get_animation(self):
        animation = self.ui.animationLineEdit.text().strip()
        return None if animation == "" else animation

    def get_topic_tag(self):
        topic_tag = TopicTag()
        if self.ui.topicTab.isEnabled():
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

    def get_module(self):
        tab_index = self.ui.tabWidget.indexOf(self.ui.tabWidget.findChild(QtWidgets.QWidget, 'moduleTab'))
        if self.ui.tabWidget.isTabEnabled(tab_index):
            design_module = DesignModule()

            # name
            module_name = "{}".format(self.ui.moduleNameComboBox.currentText())
            if module_name in InteractionModule.keys():
                self.logger.info(f"Module name set to: {module_name}")
                design_module.name = module_name

            # filename
            if self.ui.moduleFileRadioButton.isChecked():
                design_module.filename = "{}".format(self.ui.moduleFileNameLineEdit.text())
            elif self.ui.moduleRandomizeRadioButton.isChecked():
                design_module.randomize = True
                design_module.folder_name = "{}".format(self.ui.moduleFolderNameLineEdit.text())

            self.logger.info(design_module.to_dict)
            return design_module

        return None

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

            if playlist == "" or playlist in SELECT_OPTION \
                    or track == "" or track in SELECT_OPTION:
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
        d_block.pattern = "{}".format(self.ui.patternLineEdit.text().strip())
        d_block.description = "{}".format(self.ui.blockDescriptionLineEdit.text().strip())
        d_block.speech_act = self.get_speech_act()
        d_block.animation = self.get_animation()
        d_block.topic_tag = self.get_topic_tag()
        d_block.tablet_page = self.get_tablet_page()
        d_block.action_command = self.get_command()
        d_block.design_module = self.get_module()
        # d_block.interaction_module_name = self.get_module()

        return d_block

    def update_interaction_block(self, int_block):
        if int_block is None:
            return

        int_block.name = "{}".format(self.ui.patternLineEdit.text().strip())
        int_block.pattern = "{}".format(self.ui.patternLineEdit.text().strip())
        if int_block.block:
            int_block.block.title = int_block.pattern.title()
        int_block.description = "{}".format(self.ui.blockDescriptionLineEdit.text().strip())
        int_block.speech_act = self.get_speech_act()
        int_block.animation = self.get_animation()
        int_block.topic_tag = self.get_topic_tag()
        int_block.tablet_page = self.get_tablet_page()
        int_block.design_module = self.get_module()
        # int_block.interaction_module_name = self.get_module()

        # don't update music command if there is no connection to the music service
        if "{}".format(self.ui.actionComboBox.currentText()) == ActionCommand.PLAY_MUSIC.name:
            if self.music_controller is not None:
                int_block.action_command = self.get_command()
        else:
            int_block.action_command = self.get_command()

    def _is_valid_option(self, option):
        if option is not None and option != "" and option != SELECT_OPTION:
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
