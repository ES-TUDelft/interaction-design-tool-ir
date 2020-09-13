#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================== #
# SCENE_HISTORY_CONTROLLER #
# ======================== #
# Class for controlling the scene's history (to allow undo/redo operations).
#
# @author ES
# **

from block_manager.controller.history_controller import HistoryController


class SceneHistoryController(HistoryController):
    def __init__(self, scene):
        super(SceneHistoryController, self).__init__()

        self.scene = scene

    def create_stamp(self, description):
        return {
            "description": description,
            "snapshot": self.scene.serialize()
        }

    def restore_stamp(self, stamp):
        try:
            self.scene.clear()

            self.scene.deserialize(stamp["snapshot"])
            self.scene.clear_selection()

        except Exception as e:
            self.logger.error("Error while restoring history! {}".format(e))

