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
        self.session.call("rom.optional.behavior.play", name="BlocklyStand")

    def reset_posture(self):
        self.session.call("rom.optional.behavior.play", name="BlocklyStand")

    def is_awake(self):
        return True

    def rest(self):
        self.session.call("rom.optional.behavior.play", name="BlocklyCrouch")

    def set_posture(self, posture_name):
        self.session.call("rom.optional.posture.goto", name="Stand" if posture_name is None else posture_name)

    def execute_animation(self, animation_name):
        self.session.call("rom.optional.behavior.play", name="{}".format(animation_name))

    def move_to(self, x=0, y=0, theta=0):
        pass
