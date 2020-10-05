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

from twisted.internet.defer import inlineCallbacks


class AnimationHandler(object):
    def __init__(self, session):
        self.logger = logging.getLogger("AnimationHandler")

        self.session = session
        self.logger.info("Created animation handler")

    @inlineCallbacks
    def wakeup(self):
        yield self.session.call("rom.optional.behavior.play", name="BlocklyStand")

    @inlineCallbacks
    def reset_posture(self):
        yield self.session.call("rom.optional.behavior.play", name="BlocklyStand")

    @inlineCallbacks
    def rest(self):
        yield self.session.call("rom.optional.behavior.play", name="BlocklyCrouch")

    @inlineCallbacks
    def set_posture(self, posture_name):
        yield self.session.call("rom.optional.posture.goto", name="Stand" if posture_name is None else posture_name)

    @inlineCallbacks
    def execute_animation(self, animation_name):
        yield self.session.call("rom.optional.behavior.play", name="{}".format(animation_name))
