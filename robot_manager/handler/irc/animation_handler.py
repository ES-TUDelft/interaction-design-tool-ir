#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================= #
# ANIMATION_HANDLER #
# ================= #
# Handler class for animating the robot (controlling its behaviors)
#
# @author ES
# **

import logging


class AnimationHandler(object):
    def __init__(self, session):
        self.logger = logging.getLogger("AnimationHandler")

        self.session = session
        self.logger.info("Created animation handler")

    def wakeup(self):
        self.session.call("rom.optional.behavior.wakeup")

    def reset_posture(self):
        self.session.call("rom.optional.behavior.play", name="BlocklyStand")

    def rest(self):
        self.session.call("rom.optional.behavior.rest")

    def set_posture(self, posture_name):
        self.session.call("rom.optional.posture.goto", name="Stand" if posture_name is None else posture_name)

    def execute_animation(self, animation_name):
        return self.session.call("rom.optional.behavior.play", name="" if animation_name is None else animation_name)

    def on_animation_event(self, val=None):
        self.logger.info("Finished executing the animation.")
