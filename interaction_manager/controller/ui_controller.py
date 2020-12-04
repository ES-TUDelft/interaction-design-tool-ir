#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============= #
# UI_CONTROLLER #
# ============= #
# Class for controlling the main dialog GUI.
#
# @author ES
# **

import logging

from block_manager.utils import config_helper as bconfig_helper
from es_common.enums.robot_enums import RobotLanguage
from es_common.model.interaction_design import InteractionDesign
from es_common.utils import data_helper
from es_common.utils.qt import QtCore, QtGui, QtWidgets, qtSlot
from interaction_manager.controller.database_controller import DatabaseController
from interaction_manager.controller.es_block_controller import ESBlockController
from interaction_manager.controller.graph_widget_controller import GraphWidgetController
from interaction_manager.controller.interaction_controller import InteractionController
from interaction_manager.controller.music_controller import MusicController
from interaction_manager.controller.simulation_controller import SimulationController
from interaction_manager.controller.ui_confirmation_dialog_controller import UIConfirmationDialogController
from interaction_manager.controller.ui_edit_block_controller import UIEditBlockController
from interaction_manager.controller.ui_export_blocks_controller import UIExportBlocksController
from interaction_manager.controller.ui_import_blocks_controller import UIImportBlocksController
from interaction_manager.controller.ui_robot_connection_controller import UIRobotConnectionController
from interaction_manager.controller.ui_save_as_controller import UISaveAsController
from interaction_manager.controller.ui_spotify_connection_controller import UISpotifyConnectionController
from interaction_manager.view.ui_dialog import Ui_DialogGUI

SELECT_OPTION = "-- SELECT --"


class UIController(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(UIController, self).__init__(parent)

        self.logger = logging.getLogger("UIController")

        self.start_time = 0.0
        self.selected_block = None
        self.copied_block = None

        self.volume = 50.0
        self.volume_increase = 5.0

        self.right_click_menu = None

        self.database_controller = None
        self.block_controller = None
        self.interaction_controller = None
        self.simulation_controller = None
        self.music_controller = None

        # load stylesheet
        bconfig_helper.load_stylesheet()

        # TODO: replace by mode enums for simulation - playing - idle
        self.is_simulation_mode = False

        # init UI elements
        self._init_ui()

        self.filename = None
        self.load_backup_file()
        self.update()

    def _init_ui(self):
        self.ui = Ui_DialogGUI()
        self.ui.setupUi(self)

        # init controllers
        self._setup_block_manager()
        self._setup_interaction_controller()
        self._setup_simulation_controller()

        # Attach action listeners
        # CONNECTIONS
        # ===========
        self.ui.actionMenuConnect.triggered.connect(self.robot_connect)
        self.ui.actionMenuDisconnect.triggered.connect(self.robot_disconnect)
        self.ui.actionMenuDatabaseConnect.setEnabled(True)
        self.ui.actionMenuDatabaseConnect.triggered.connect(self.database_connect)
        self.ui.actionMenuDatabaseDisconnect.triggered.connect(self.database_disconnect)
        # ROBOT POSTURE
        # -------------
        self.ui.actionMenuWakeUp.triggered.connect(self.wakeup)
        self.ui.actionMenuRest.triggered.connect(self.rest)
        # TOUCH
        # ------
        self.ui.actionMenuEnableTouch.triggered.connect(self.enable_touch)
        # TABLET
        # ------
        self.ui.actionMenuShowImage.triggered.connect(self.show_image_on_tablet)
        self.ui.actionMenuHideImage.triggered.connect(self.hide_image_on_tablet)
        # INTERACTION PLAY/SIMULATION
        # ---------------------------
        self.ui.actionMenuPlay.setEnabled(False)
        self.ui.actionMenuPlay.triggered.connect(self.play_blocks)
        self.ui.actionMenuSimulate.triggered.connect(self.simulate_blocks)
        self.ui.actionMenuStop.triggered.connect(self.interaction_controller.stop_playing)
        self.ui.actionMenuEngage.triggered.connect(lambda: self.interaction_controller.engagement(start=True))
        # MUSIC
        # --------
        self.ui.actionMenuMusic.triggered.connect(self.spotify_connect)
        self.ui.musicPlaylistComboBox.currentIndexChanged.connect(self.update_tracks_combo)
        self.ui.musicTracksComboBox.currentIndexChanged.connect(self.enable_music_buttons)
        self.ui.musicPlayButton.clicked.connect(self.play_music)
        self.ui.musicPauseButton.clicked.connect(self.pause_music)
        self.ui.musicVolumeButton.clicked.connect(self.music_volume)
        # VOLUME
        self.ui.actionMenuVolumeUp.triggered.connect(self.volume_up)
        self.ui.actionMenuVolumeDown.triggered.connect(self.volume_down)

        # SETTINGS
        # ---------
        self._init_settings_widget()

        # Graph
        self._init_graph_widget()

        # UNDO/REDO
        # ---------
        self.ui.actionMenuUndo.triggered.connect(self.on_undo)
        self.ui.actionMenuRedo.triggered.connect(self.on_redo)
        # CLEAR/DELETE
        # ============
        self.ui.actionMenuClear.triggered.connect(self.clear_blocks)
        self.ui.actionMenuDelete.triggered.connect(self.on_delete)
        # ZOOM
        # ============
        # self.ui.actionMenuZoomIn.setShortcut("Ctrl+-")
        self.ui.actionMenuZoomIn.triggered.connect(lambda: self.on_zoom(1))
        self.ui.actionMenuZoomOut.triggered.connect(lambda: self.on_zoom(-1))
        # COPY/PASTE
        # ----------
        # TODO: Copy block not parameters
        self.ui.actionMenuCopy.triggered.connect(self.copy_block)
        self.ui.actionMenuPaste.triggered.connect(self.paste_block)

        # DELETE, RESET, CLEAR, IMPORT and SAVE list listeners
        self._enable_buttons([self.ui.actionMenuNew],
                             enabled=False)  # disabled for now!
        self.ui.actionMenuSave.triggered.connect(self.on_save)
        self.ui.actionMenuSaveAs.triggered.connect(self.on_save_as)

        self.ui.actionMenuOpen.triggered.connect(self.import_blocks)
        # self.ui.actionMenuImportBlocks.triggered.connect(self.import_blocks)
        # self.ui.actionMenuExportBlocks.triggered.connect(self.export_blocks)

        # enable buttons
        self._toggle_buttons(is_awake=False)

    def _init_settings_widget(self):
        # Speech
        self.ui.languageComboBox.clear()
        self.ui.languageComboBox.addItems([k.title() for k in RobotLanguage.keys()])
        self.ui.languageComboBox.currentIndexChanged.connect(
            lambda: self.update_setting(key="robotLanguage", value=self.ui.languageComboBox.currentText()))
        self.ui.voicePitchSpinBox.valueChanged.connect(
            lambda: self.update_setting(key="voicePitch", value=float(self.ui.voicePitchSpinBox.value())))
        self.ui.voiceSpeedSpinBox.valueChanged.connect(
            lambda: self.update_setting(key="voiceSpeed", value=float(self.ui.voiceSpeedSpinBox.value())))
        self.ui.speechCertaintySpinBox.valueChanged.connect(
            lambda: self.update_setting(key="speechCertainty", value=float(self.ui.speechCertaintySpinBox.value())))
        # Engagement
        self.ui.faceSizeDoubleSpinBox.valueChanged.connect(
            lambda: self.update_setting(key="faceSize", value=round(float(self.ui.faceSizeDoubleSpinBox.value()), 2)))
        self.ui.interactionIntervalSpinBox.valueChanged.connect(
            lambda: self.update_setting(key="interactionInterval",
                                        value=float(self.ui.interactionIntervalSpinBox.value())))
        self.ui.disengagementIntervalSpinBox.valueChanged.connect(
            lambda: self.update_setting(key="disengagementInterval",
                                        value=float(self.ui.disengagementIntervalSpinBox.value())))

    def _init_graph_widget(self):
        self.graph_widget_controller = GraphWidgetController(self.ui.plotWidget)
        self.interaction_controller.face_detected_signal.connect(self.graph_widget_controller.append_data)

    def _setup_block_manager(self):
        self.block_controller = ESBlockController(parent_widget=self)

        # remove tmp widget and setup the blocks controller
        self.ui.designPanelLayout.removeWidget(self.ui.tmpWidget)

        # add design widget in the middle
        self.ui.designPanelLayout.addWidget(self.block_controller.block_widget)

        # add dock list widget
        self.block_dock_widget = self.block_controller.create_block_dock()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.block_dock_widget)
        self.tabifyDockWidget(self.ui.blocksDockWidget, self.block_dock_widget)
        self.removeDockWidget(self.ui.blocksDockWidget)

        # action listeners
        self.ui.actionMenuLogs.triggered.connect(lambda: self.ui.logsDockWidget.setHidden(False))
        self.ui.actionMenuBlockList.triggered.connect(lambda: self.block_dock_widget.setHidden(False))
        self.ui.actionMenuSimulationDockView.triggered.connect(lambda: self.simulation_dock_widget.setHidden(False))
        self.ui.actionMenuMusicDockView.triggered.connect(lambda: self.ui.musicDockWidget.setHidden(False))
        self.ui.actionMenuSettingsDockView.triggered.connect(lambda: self.ui.settingsDockWidget.setHidden(False))

        # observe selected blocks
        self.block_controller.block_selected_observers.add_observer(self.on_block_selected)
        self.block_controller.no_block_selected_observers.add_observer(self.on_no_block_selected)
        self.block_controller.start_block_observers.add_observer(self.on_invalid_action)
        self.block_controller.invalid_edge_observers.add_observer(self.on_invalid_action)
        self.block_controller.scene_change_observers.add_observer(self.on_scene_change)
        # self.block_controller.block_settings_observers.add_observer(self.block_settings)
        self.block_controller.block_editing_observers.add_observer(self.block_editing)
        self.block_controller.right_click_block_observers.add_observer(self.create_popup_menu)

    def _setup_interaction_controller(self):
        self.interaction_controller = InteractionController(block_controller=self.block_controller)
        self.interaction_controller.has_finished_playing_observers.add_observer(self.on_finished_playing)

    def _setup_simulation_controller(self):
        self.simulation_controller = SimulationController(self.block_controller, parent=self)
        # add dock list widget
        self.simulation_dock_widget = self.simulation_controller.simulation_dock_widget
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.simulation_dock_widget)
        self.tabifyDockWidget(self.ui.logsDockWidget, self.simulation_dock_widget)
        self.tabifyDockWidget(self.simulation_dock_widget, self.ui.musicDockWidget)
        self.tabifyDockWidget(self.ui.musicDockWidget, self.ui.settingsDockWidget)
        self.tabifyDockWidget(self.ui.settingsDockWidget, self.ui.graphDockWidget)

        # activate logs panel
        self.ui.logsDockWidget.setFocus()
        self.ui.logsDockWidget.raise_()

        # observer
        self.simulation_controller.finished_simulation_observable.add_observer(self.on_finished_simulation)

    def exit_gracefully(self):
        self.logger.info("Exiting...")
        # add any other disconnection calls...
        self.interaction_controller.on_exit()

    # ---------- #
    # Connection
    # ---------- #
    @qtSlot()
    def robot_connect(self):
        try:
            connection_dialog = UIRobotConnectionController(self.interaction_controller)

            if connection_dialog.exec_():
                if connection_dialog.success is True:
                    self.logger.debug("Robot is_awake = {}".format(connection_dialog.is_awake))
                    self._toggle_buttons(is_awake=False)

                    self._enable_buttons([self.ui.actionMenuConnect], enabled=False)
                    self._enable_buttons([self.ui.actionMenuDisconnect], enabled=True)

                    self._update_interaction_settings()

                    self._display_message(message="Successfully connected to the robot.")
                else:
                    self._enable_buttons([self.ui.actionMenuConnect], enabled=True)
                    self._enable_buttons([self.ui.actionMenuDisconnect], enabled=False)
                    self._display_message(error="Unable to connect!")
            else:
                self._display_message(error="Connection is canceled!")
                # if self.interaction_controller.is_connected() is False:
                #     self.robot_disconnect()
        except Exception as e:
            self._display_message(error="Error while attempting to connect to the robot! {}".format(e))

    @qtSlot()
    def robot_disconnect(self):
        try:
            self.interaction_controller.disconnect()

            # update GUI
            # self._toggle_buttons(is_awake=False)
            self._enable_buttons([self.ui.actionMenuConnect], enabled=True)
            self._enable_buttons([self.ui.actionMenuDisconnect], enabled=False)
            self._display_message(message="### Disconnected from the robot.")
        except Exception as e:
            self._display_message(error="Error while attempting to disconnect from the robot! {}".format(e))

    # --------- #
    # MONGO DB
    # --------- #
    @qtSlot()
    def database_connect(self):
        self.database_controller = DatabaseController()

        message, error = self.database_controller.connect()

        if error is None:
            self._enable_buttons([self.ui.actionMenuDatabaseDisconnect],
                                 enabled=True)
            self._enable_buttons([self.ui.actionMenuDatabaseConnect], enabled=False)
            self._display_message(message=message)
        else:
            self._display_message(error=error)

    @qtSlot()
    def database_disconnect(self):

        self._enable_buttons([self.ui.actionMenuDatabaseDisconnect],
                             enabled=False)
        self._enable_buttons([self.ui.actionMenuDatabaseConnect], enabled=True)

        if self.database_controller is None:
            self._display_message(message='Database was already disconnected')
        else:
            message, error = self.database_controller.disconnect()
            if error is None:
                self._display_message(message=message)
            else:
                self._display_message(error=error)

    ####
    # SPOTIFY
    ###
    @qtSlot()
    def spotify_connect(self):
        try:
            if self.music_controller is None:
                self.set_music_controller(MusicController())

            spotify_dialog = UISpotifyConnectionController()

            if spotify_dialog.exec_():
                if spotify_dialog.success is True:
                    self.music_controller.username = spotify_dialog.username
                    self.music_controller.spotify = spotify_dialog.spotify
                    self.music_controller.playlists = spotify_dialog.playlists

                    self.ui.musicVolumeButton.setEnabled(True)
                    self.update_playlist_combo()
                    # set focus on the music widget
                    self.ui.musicDockWidget.setFocus()
                    self.ui.musicDockWidget.raise_()
                    self._display_message(message="Successfully connected to spotify.")
                else:
                    self.reset_music_player()
                    self._display_message(warning="Spotify is not connected!")
            else:
                self.reset_music_player()
                self._display_message(warning="Spotify is not connected!")
        except Exception as e:
            self.reset_music_player()
            self._display_message(error="Error while connecting to spotify! {}".format(e))

    def reset_music_player(self):
        self._enable_buttons([self.ui.musicVolumeButton, self.ui.musicPlayButton,
                              self.ui.musicPauseButton], enabled=False)
        self.ui.musicPlaylistComboBox.clear()
        self.ui.musicTracksComboBox.clear()
        self.set_music_controller(None)

    def set_music_controller(self, music_controller):
        self.music_controller = music_controller
        # update observers
        self.interaction_controller.music_controller = self.music_controller
        self.simulation_controller.music_controller = self.music_controller

    def update_playlist_combo(self):
        self.ui.musicPlaylistComboBox.clear()
        if self.music_controller.playlists is None or len(self.music_controller.playlists) == 0:
            return
        try:
            self.ui.musicPlaylistComboBox.addItems([SELECT_OPTION])
            self.ui.musicPlaylistComboBox.addItems([p for p in self.music_controller.playlists.keys()])
        except Exception as e:
            self._display_message(warning="Unable to load the playlists! {}".format(e))

    def update_tracks_combo(self):
        try:
            self.ui.musicTracksComboBox.clear()
            playlist = self.ui.musicPlaylistComboBox.currentText()
            if playlist == "" or playlist == SELECT_OPTION:
                return

            self.ui.musicTracksComboBox.addItems([SELECT_OPTION])
            self.ui.musicTracksComboBox.addItems([t for t in self.music_controller.playlists[playlist]["tracks"]])

            self.ui.musicPlayButton.setEnabled(False)
            self.ui.musicDockWidget.update()
        except Exception as e:
            self._display_message(warning="Unable to load tracks! {}".format(e))

    @qtSlot()
    def enable_music_buttons(self):
        if self.ui.musicTracksComboBox.currentText() != SELECT_OPTION:
            # enable play button
            self._enable_buttons([self.ui.musicPlayButton], enabled=True)
        else:
            # disable
            self._enable_buttons([self.ui.musicPlayButton], enabled=False)
        self.ui.musicDockWidget.update()

    @qtSlot()
    def play_music(self):
        try:
            self.music_volume()
            success = self.music_controller.play(playlist=self.ui.musicPlaylistComboBox.currentText(),
                                                 track=self.ui.musicTracksComboBox.currentText())
            if success:
                self.ui.musicMessageLineEdit.setText("Currently playing: {}".format(
                    self.ui.musicTracksComboBox.currentText()
                ))
                self.ui.musicPauseButton.setEnabled(True)
                self.ui.musicPlayButton.setEnabled(False)
            else:
                warning_msg = self.music_controller.warning_message
                self.ui.musicMessageLineEdit.setText("Unable to play!" if warning_msg is None else warning_msg)
                self._display_message("Error while playing {} | {}".format(self.ui.musicTracksComboBox.currentText(),
                                                                           self.music_controller.error_message))
            self.ui.musicDockWidget.update()
        except Exception as e:
            warning_msg = self.music_controller.warning_message
            self.ui.musicMessageLineEdit.setText("Unable to play!" if warning_msg is None else warning_msg)
            self._display_message("Error while playing {} | {}".format(self.ui.musicTracksComboBox.currentText(), e))

    @qtSlot()
    def pause_music(self):
        try:
            success = self.music_controller.pause()
            if success:
                self.ui.musicMessageLineEdit.setText("Paused: {}".format(
                    self.ui.musicTracksComboBox.currentText()
                ))
            self.ui.musicPauseButton.setEnabled(False)
            self.ui.musicPlayButton.setEnabled(True)
            self.ui.musicDockWidget.update()
        except Exception as e:
            self._display_message("Error while playing {} | {}".format(self.ui.musicTracksComboBox, e))

    @qtSlot()
    def music_volume(self):
        val = int(self.ui.musicVolumeSpinBox.value())
        self.music_controller.volume(val)

    # DETECTION CERTAINTY
    #####################
    def update_speech_certainty(self, val=None):
        speech_certainty = float(self.ui.speechCertaintySpinBox.value())
        self.logger.info("Updating detection certainties to: {}".format(speech_certainty))
        if self.interaction_controller:
            self.interaction_controller.update_speech_certainty(speech_certainty=speech_certainty)

    def update_setting(self, key, value):
        try:
            self.interaction_controller.update_db_data(data_key=key, data_value=value)
            self.logger.info("Updated {} to {}".format(key, value))
        except Exception as e:
            self.logger.error("Error while updating {} to {} | {}".format(key, value, e))

    def _update_interaction_settings(self):
        self.update_setting(key="speechCertainty", value=float(self.ui.speechCertaintySpinBox.value()))
        self.update_setting(key="voicePitch", value=float(self.ui.voicePitchSpinBox.value()))
        self.update_setting(key="voiceSpeed", value=float(self.ui.voiceSpeedSpinBox.value()))
        self.update_setting(key="faceSize", value=round(float(self.ui.faceSizeDoubleSpinBox.value()), 2))
        self.update_setting(key="interactionInterval",
                            value=float(self.ui.disengagementIntervalSpinBox.value()))
        self.update_setting(key="disengagementInterval",
                            value=float(self.ui.disengagementIntervalSpinBox.value()))

    # ----------- #
    # Robot Start
    # ----------- #
    @qtSlot()
    def wakeup(self):
        success = self.interaction_controller.wakeup_robot()
        self._toggle_buttons(is_awake=success)
        self._display_message(message="Robot is awake and ready for action.")

    @qtSlot()
    def rest(self):
        self.interaction_controller.rest_robot()
        self._toggle_buttons(is_awake=False)
        self._display_message(message="Robot is Resting")

    # TOUCH
    # ------
    @qtSlot()
    def enable_touch(self):
        self.interaction_controller.enable_touch()
        self._enable_buttons([self.ui.actionMenuEnableTouch], False)
        self._display_message(message="Touch sensors are enabled.")

    @qtSlot()
    def volume_up(self):
        vol = self.volume + self.volume_increase
        self.set_volume(vol)
        self._display_message("Volume set to: {}".format(self.volume))

    @qtSlot()
    def volume_down(self):
        vol = self.volume - self.volume_increase
        self.set_volume(vol)
        self._display_message("Volume set to: {}".format(self.volume))

    def set_volume(self, vol):
        if self._check_value(vol, 0.0, 100.0) is True:
            self.volume = vol
            if self.interaction_controller is not None:
                self.interaction_controller.robot_volume = vol

    # TABLET
    # ------
    @qtSlot()
    def show_image_on_tablet(self):
        self.interaction_controller.tablet_image(hide=False)
        self._enable_buttons([self.ui.actionMenuShowImage], enabled=False)
        self._enable_buttons([self.ui.actionMenuHideImage], enabled=True)
        self._display_message(message="Updating tablet's image")

    @qtSlot()
    def hide_image_on_tablet(self):
        self.interaction_controller.tablet_image(hide=True)
        self._enable_buttons([self.ui.actionMenuShowImage], enabled=True)
        self._enable_buttons([self.ui.actionMenuHideImage], enabled=False)
        self._display_message(message="Hiding tablet's image")

    def verify_interaction_setup(self):
        # check if the scene contains a valid start block
        block = self.block_controller.get_block(pattern="start")
        if block is None:
            self._display_message(error="The scene doesn't contain a starting block! "
                                        "Please add a 'START' block then click on play")
        return block

    @qtSlot()
    def simulate_blocks(self):
        if self.simulation_controller is None:
            self._setup_simulation_controller()

        # set simulation music_controller
        self.simulation_controller.music_controller = self.music_controller

        block = self.verify_interaction_setup()
        if block is not None:
            self.is_simulation_mode = True
            self._enable_buttons([self.ui.actionMenuSimulate], enabled=False)
            self._display_message(message="Attempting to simulate the interaction!")
            self.simulation_controller.start_simulation(int_block=block.parent)

    def keyPressEvent(self, event):
        if self.is_simulation_mode is True \
                and event.key() == QtCore.Qt.Key_BracketRight and event.modifiers() & QtCore.Qt.ControlModifier:
            self.simulation_controller.execute_next_interaction_block()

        super(UIController, self).keyPressEvent(event)

    @qtSlot()
    def play_blocks(self):
        # if yes, send the request to the interaction controller
        block = self.verify_interaction_setup()
        if block is not None:
            self._display_message(message="Attempting to play the interaction!")

            # set Language
            self.update_setting(key="robotLanguage", value=self.ui.languageComboBox.currentText())

            self._enable_buttons([self.ui.actionMenuPlay], enabled=False)
            self._enable_buttons([self.ui.actionMenuStop], enabled=True)
            self.interaction_controller.robot_volume = self.volume

            # Start
            self.interaction_controller.is_interacting = True
            self.interaction_controller.start_playing(int_block=block.parent)

    def on_finished_playing(self, event):
        try:
            self._enable_buttons([self.ui.actionMenuPlay], enabled=True)
            # self._enable_buttons([self.ui.actionMenuStop], enabled=False)

            # insert executed blocks in DB
            if self.database_controller:
                interaction_design = InteractionDesign()
                for i in range(len(self.interaction_controller.executed_blocks)):
                    interaction_design.blocks["{}".format(i)] = self.interaction_controller.executed_blocks[i].to_dict
                # interaction_design.face_size = self.interaction_controller.face_size_dict
                # self.logger.info(interaction_design.to_dict)
                self.insert_design_in_db(interaction_design)

            self.interaction_controller.reset()
        except Exception as e:
            self.logger.error("Warning while enabling the buttons: {}".format(e))

    def on_finished_simulation(self, event):
        self._enable_buttons([self.ui.actionMenuSimulate], enabled=True)
        self.is_simulation_mode = False

    # ----------------
    # Block Listeners:
    # ----------------
    def on_invalid_action(self, val):
        self._display_message(warning="{}".format(val))

    def on_scene_change(self, val):
        # backup scene
        self.backup_blocks()

    def on_block_selected(self, block):
        self.selected_block = block
        # enable/disable copy/paste
        self._enable_buttons([self.ui.actionMenuCopy], enabled=True)

        self.logger.info("Received notification for 'block selected', refreshing GUI now!")
        self.update_gui()

    def on_no_block_selected(self, event):
        self.selected_block = None

        # disable copy/paste
        self._enable_buttons([self.ui.actionMenuCopy, self.ui.actionMenuPaste],
                             enabled=False)
        self.update_gui()

    def block_editing(self, block):
        if block is None:
            return

        self.selected_block = block
        try:
            # Open edit dialog
            edit_dialog = UIEditBlockController(interaction_block=self.selected_block.parent,
                                                block_controller=self.block_controller,
                                                music_controller=self.music_controller,
                                                robot_controller=self.get_robot_controller())

            if edit_dialog.exec_():
                edit_dialog.update_interaction_block(self.selected_block.parent)

                self.block_controller.store("Edited block")
                self.update_gui()
        except Exception as e:
            self._display_message(error="Error while attempting to edit the block! {}".format(e))

    @qtSlot()
    def copy_block(self):
        if self.selected_block is not None:
            self.copied_block = self.selected_block
            # self.enable_paste_buttons()

    @qtSlot()
    def paste_block(self):
        # if self.selected_block is not None and self.copied_block is not None:
        #     # TODO
        # self.block_controller.store("Updated parameters")
        self._display_message(warning="Not Implemented.")

    def enable_paste_buttons(self):
        self._enable_buttons([self.ui.actionMenuPaste],
                             enabled=False if self.copied_block is None else True)

    #
    # MENU ACTIONS
    # ============
    @qtSlot()
    def on_file_new(self):
        self.block_controller.clear_scene()

    @qtSlot()
    def on_undo(self):
        self.block_controller.undo()
        self.on_no_block_selected(None)

    @qtSlot()
    def on_redo(self):
        self.block_controller.redo()
        self.on_no_block_selected(None)

    @qtSlot()
    def on_delete(self):
        self.block_controller.delete_selected()

    @qtSlot(int)
    def on_zoom(self, val):
        self.block_controller.zoom_scene(val=val)

    # -------------------- #
    # Interaction Block Lists
    # -------------------- #
    def create_popup_menu(self, event):
        """
        Creates a popup menu when the user right-clicks on a block
        """
        self.right_click_menu = QtWidgets.QMenu(self)

        item = self.block_controller.get_item_at(event.pos())

        if hasattr(item, "block"):
            self.logger.debug("item has block attribute: {}".format(item))

            block = item.block
            block.set_selected(val=True)

            # enable widget
            # TODO: enable right click menu

            # Add an edit block action
            self.right_click_menu.addAction("Edit")

            # Add a separator
            self.right_click_menu.addSeparator()

            # Add a delete block action
            self.right_click_menu.addAction("Delete")

            # Add a separator
            self.right_click_menu.addSeparator()

            # TODO: Add a duplicate option
            # self.right_click_menu.addAction("Duplicate")

            # TODO:
            action = self.right_click_menu.exec_(self.block_controller.get_block_widget().mapToGlobal(
                event.pos()))  # self.block_controller.get_block_widget(), event.pos()))
            if action:
                self.execute_right_click_action(action, block)

    def execute_right_click_action(self, action, block):
        """
        Function that executes popup menu actions
        """
        action_name = "{}".format(action.text())
        if action_name == "Edit":
            self.block_editing(block)
        elif action_name == "Copy Settings":
            self.copy_block()
        elif action_name == "Delete":
            self.on_delete()
        elif action_name == "Duplicate":
            pass  # self.duplicate_block()

    def duplicate_block(self):
        # TODO: implement duplicating a block
        self._display_message(message="Successfully duplicated the block.")
        # backup
        self.backup_blocks()

    @qtSlot()
    def clear_blocks(self):
        # Ask for confirmation
        confirmation_dialog = UIConfirmationDialogController(message="All blocks will be deleted!")
        if confirmation_dialog.exec_():
            self.block_controller.clear_scene()

    def insert_design_in_db(self, interaction_design):
        success = self.database_controller.insert_interaction_design(design_dict=interaction_design.to_dict)
        if success is True:
            self._display_message(message="Successfully inserted the selected interaction blocks.")
        else:
            self._display_message(error="Error while inserting interaction blocks.")

    @qtSlot()
    def export_blocks(self):
        interaction_design = self.block_controller.get_serialized_scene()

        # open export dialog
        export_dialog = UIExportBlocksController(serialized_data=interaction_design)
        if export_dialog.exec_():
            self._display_message(message="Successfully exported the interaction blocks.")

    def load_backup_file(self):
        try:
            filename = data_helper.get_backup_filename()
            blocks_data = data_helper.load_data_from_file(filename)
            self.block_controller.load_blocks_data(blocks_data)
            self.logger.info("Loaded backup data.")
        except Exception as e:
            self.logger.error("Error while loading backup: {}".format(e))

    def backup_blocks(self):
        filename = data_helper.get_backup_filename()
        self.block_controller.save_blocks(filename=filename)
        self._update_filename_label(is_modified=True)

    @qtSlot()
    def on_save(self):
        if self.filename is None:
            self.on_save_as()
        else:
            self.save_blocks()

    def save_blocks(self):
        if self.filename is None:
            self.logger.warning("Select a file to save the design.")
        else:
            # filename = "{}/logs/blocks_{}.json".format(os.getcwd(), date_helper.get_day_and_month())
            success = self.block_controller.save_blocks(filename=self.filename)
            self._update_filename_label()
            if success:
                self._display_message(message="Successfully saved the blocks!")
            else:
                self._display_message(error="Error while saving the blocks!")

    @qtSlot()
    def on_save_as(self):
        # open save_as dialog
        save_as_dialog = UISaveAsController()
        if save_as_dialog.exec_():
            filename = save_as_dialog.get_full_path()
            try:
                data_helper.save_to_file(filename=filename,
                                         serialized_data=self.block_controller.get_serialized_scene())
                self.filename = filename
                self._display_message(message="Successfully saved the design.")
            except Exception as e:
                self._display_message("Error while saving design data to: {} | {}".format(filename, e))
        else:
            self._display_message(message="SaveAs is Cancelled!")

    @qtSlot()
    def import_blocks(self):
        # open import dialog
        import_dialog = UIImportBlocksController()

        if import_dialog.exec_():
            if import_dialog.blocks_data is None or len(import_dialog.blocks_data) == 0:
                return
            # fill scene with blocks
            self.block_controller.load_blocks_data(data=import_dialog.blocks_data)

            self.filename = import_dialog.ui.fileNameLineEdit.text()
            self._update_filename_label()
            self._display_message(message="New blocks are imported.")

    ###
    # HELPER METHODS
    ###
    def update_gui(self):
        self.block_controller.update_widget()
        self.repaint()
        # QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        # QTest.qWait(1)

    def get_robot_controller(self):
        if self.interaction_controller is None:
            return None
        return None  # self.interaction_controller.robot_controller

    def _check_value(self, value, start, stop):
        if start <= value <= (stop + 1):
            return True
        else:
            self.logger.error("*** Please provide a value in range: [{}, {}]".format(start, stop))
            return False

    def _display_message(self, message=None, error=None, warning=None):
        if error is None:
            # check if we have a warning or a normal message
            c = QtGui.QColor("white") if warning is None else QtGui.QColor("orange")
            to_display = message if message is not None else warning
            self.logger.info(to_display)
        else:
            c = QtGui.QColor("red")
            to_display = error
            self.logger.error(to_display)

        self.ui.logsTextEdit.setTextColor(c)
        self.ui.logsTextEdit.append(to_display)

        self.update()

    def _enable_buttons(self, buttons=None, enabled=False):
        if buttons is None:
            return

        for button in buttons:
            try:
                button.setEnabled(enabled)
                button.setChecked(False)
            except Exception as e:
                self.logger.info("Error while enabling button: {} | {}".format(button, e))
            finally:
                pass

    def _toggle_widget(self, widget, btns=None, enable=True):
        if btns is None:
            return

        widget.setEnabled(enable)
        self._enable_buttons(buttons=btns, enabled=enable)

    def _toggle_buttons(self, is_awake=False):
        if is_awake is True:
            # Enable/disable buttons
            self._enable_buttons([self.ui.actionMenuWakeUp, self.ui.actionMenuRest, self.ui.actionMenuShowImage,
                                  self.ui.actionMenuEnableTouch,
                                  self.ui.actionMenuVolumeDown, self.ui.actionMenuVolumeUp,
                                  self.ui.actionMenuPlay, self.ui.actionMenuEngage, self.ui.actionMenuStop
                                  ], enabled=True)
            self._enable_buttons([self.ui.actionMenuHideImage], enabled=False)
        else:
            # Enable wake up button
            self._enable_buttons([self.ui.actionMenuWakeUp], enabled=True)
            # disable everything
            self._enable_buttons([self.ui.actionMenuRest, self.ui.actionMenuShowImage, self.ui.actionMenuHideImage,
                                  self.ui.actionMenuEnableTouch,
                                  self.ui.actionMenuVolumeDown, self.ui.actionMenuVolumeUp, self.ui.actionMenuPlay,
                                  self.ui.actionMenuEngage, self.ui.actionMenuStop,
                                  ], enabled=False)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename
        self._update_filename_label()

    def _update_filename_label(self, is_modified=False):
        if self.filename:
            self.ui.filenameLabel.setText("{}{}".format(self.filename, "*" if is_modified else ""))
