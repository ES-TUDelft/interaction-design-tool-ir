#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========================= #
# UI_PARAMETERS_CONTROLLER #
# ========================= #
# Class for controlling the block editor GUI.
#
# @author ES
# **

import logging

from PyQt5 import QtWidgets, QtGui

import es_common.hre_config as pconfig
from es_common.enums.led_enums import LedColor
from es_common.enums.speech_enums import GazePattern, GesturesType
from es_common.enums.voice_enums import VoiceProsody
from interaction_manager.controller.ui_confirmation_dialog_controller import UIConfirmationDialogController
from interaction_manager.view.ui_parameters_dialog import Ui_ParametersDialog


class UIParametersController(QtWidgets.QDialog):
    def __init__(self, interaction_block, block_controller, interaction_controller=None, parent=None):
        super(UIParametersController, self).__init__(parent)

        self.logger = logging.getLogger("EditBlockController")

        self.interaction_block = interaction_block
        self.behavioral_parameters = self.interaction_block.behavioral_parameters.clone()

        self.block_controller = block_controller
        self.interaction_controller = interaction_controller

        # init UI elements
        self.ui = Ui_ParametersDialog()
        self.ui.setupUi(self)

        # init ui elements
        self._init_ui()

        # give it control
        self.setModal(True)

    def _init_ui(self):
        # group eye color buttons
        self.eye_color_radio_buttons = [self.ui.whiteEyeColorRadioButton, self.ui.redEyeColorRadioButton,
                                        self.ui.greenEyeColorRadioButton, self.ui.blueEyeColorRadioButton]

        # Eye color listeners
        self.ui.whiteEyeColorRadioButton.toggled.connect(lambda: self.eye_color(self.ui.whiteEyeColorRadioButton))
        self.ui.redEyeColorRadioButton.toggled.connect(lambda: self.eye_color(self.ui.redEyeColorRadioButton))
        self.ui.greenEyeColorRadioButton.toggled.connect(lambda: self.eye_color(self.ui.greenEyeColorRadioButton))
        self.ui.blueEyeColorRadioButton.toggled.connect(lambda: self.eye_color(self.ui.blueEyeColorRadioButton))

        # Listeners
        self.ui.gestureOpennessSlider.valueChanged.connect(lambda: self.gesture_openness(self.ui.gestureOpennessSlider))
        self.ui.gazePatternSlider.valueChanged.connect(lambda: self.gaze_pattern(self.ui.gazePatternSlider))
        self.ui.proxemicsSlider.valueChanged.connect(lambda: self.proxemics(self.ui.proxemicsSlider))
        self.ui.voicePitchSlider.valueChanged.connect(lambda: self.voice_pitch(self.ui.voicePitchSlider))
        self.ui.voiceSpeedSlider.valueChanged.connect(lambda: self.voice_speed(self.ui.voiceSpeedSlider))
        self.ui.voiceProsodySlider.valueChanged.connect(lambda: self.voice_prosody(self.ui.voiceProsodySlider))

        # TEST button
        self.ui.testBehavioralParametersButton.clicked.connect(self.test_behavioral_parameters)
        self.ui.testBehavioralParametersButton.setEnabled(
            False if self.interaction_controller is None else self.interaction_controller.is_connected()
        )
        # Apply button
        self.ui.behavioralParametersApplyToAllButton.clicked.connect(self.apply_behavioral_parameters)

        self.reset_parameters()

        self.repaint()

    def reset_parameters(self):
        self.ui.gestureOpennessSlider.setValue(self.behavioral_parameters.gestures_type.value)
        self.ui.gazePatternSlider.setValue(self.behavioral_parameters.gaze_pattern.value)
        # roll back the proxemics value
        self.ui.proxemicsSlider.setValue(
            self._convert_proxemics(value=self.behavioral_parameters.proxemics, to_int=True))
        self.ui.proxemicsLcdNumber.display(self.behavioral_parameters.proxemics)
        self.ui.voicePitchSlider.setValue(int(round((self.behavioral_parameters.voice.pitch - 1) / .1, 1)))
        self.ui.voiceSpeedSlider.setValue(int((self.behavioral_parameters.voice.speed - 100) / 10))
        self.ui.voiceProsodySlider.setValue(self.behavioral_parameters.voice.prosody.value)
        self._check_eye_color_btn(color=self.behavioral_parameters.eye_color)

        # reset warning label
        self._set_warning_label_color(reset=True)

    def test_behavioral_parameters(self):
        if self.interaction_controller is None:
            return

        message, error = self.interaction_controller.test_behavioral_parameters(self.interaction_block,
                                                                                self.behavioral_parameters,
                                                                                self.interaction_block.volume)
        self.display_message(message=message, error=error)

    # ---------------------
    # PARAMETERS
    # ---------------------
    def gesture_openness(self, slider):
        val = slider.value() if slider.value() in GesturesType.values() else 0
        self.behavioral_parameters.gestures_type = GesturesType(val)
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def gaze_pattern(self, slider):
        val = slider.value() if slider.value() in GazePattern.values() else 0
        self.behavioral_parameters.gaze_pattern = GazePattern(val)
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def voice_prosody(self, slider):
        val = slider.value() if slider.value() in VoiceProsody.values() else 0
        self.behavioral_parameters.voice.prosody = VoiceProsody(val)
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def voice_pitch(self, slider):
        self.behavioral_parameters.voice.pitch = (float(slider.value()) * 0.1) + 1
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def voice_speed(self, slider):
        self.behavioral_parameters.voice.speed = (float(slider.value()) * 10) + 100
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def proxemics(self, slider):
        p_val = self._convert_proxemics(value=float(slider.value()), to_float=True)
        self.ui.proxemicsLcdNumber.display(p_val)
        self.behavioral_parameters.proxemics = p_val
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def eye_color(self, btn):
        self.behavioral_parameters.eye_color = LedColor[btn.text().upper()]
        self._set_warning_label_color(c=pconfig.warning_color_rgb)

    def apply_behavioral_parameters(self):
        try:
            confirmation_dialog = UIConfirmationDialogController(
                message="The changes will be applied to all items.")
            if confirmation_dialog.exec_():
                self.block_controller.update_blocks_behavioral_parameters(
                    param_name="All",
                    behavioral_parameters=self.behavioral_parameters)
                # reset warning
                self._set_warning_label_color(reset=True)
                self.display_message(message="The parameters of all blocks are updated.")

                self.block_controller.store("Updated parameters for all blocks.")
        except Exception as e:
            self.logger.error("Error while applying the parameters! {}".format(e))

        self.repaint()

    def _set_warning_label_color(self, c=None, reset=False):
        if c is None or c == "" or reset is True:
            c = pconfig.default_color_rgb
        self.ui.warningLabel.setStyleSheet("QLabel { color : " + c + "; }")

    def _convert_proxemics(self, value=0.0, to_int=False, to_float=False):
        if to_int is True:
            return int((value - pconfig.proxemics_initial_value) / pconfig.proxemics_multiplier)
        elif to_float is True:
            return float(value * pconfig.proxemics_multiplier) + pconfig.proxemics_initial_value
        else:
            return 1

    def _check_eye_color_btn(self, color=LedColor.WHITE):
        try:
            for btn in self.eye_color_radio_buttons:
                if btn.text().lower() == color.name.lower():
                    btn.setChecked(True)
                    return
        except Exception as e:
            self.logger.info("Error while checking radio buttons! {}".format(e))

    def display_message(self, message=None, error=None):
        if message is None:
            # self.ui.messageTextEdit.setTextColor(QtGui.QColor('red'))  # red text for errors
            # self.ui.messageTextEdit.setText(error)
            self.logger.error(error)
        else:
            # self.ui.messageTextEdit.setTextColor(QtGui.QColor('white'))
            # self.ui.messageTextEdit.setText(message)
            self.logger.debug(message)

        self.repaint()
