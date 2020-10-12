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
        self.motion = self.session.service("ALMotion")
        self.posture = self.session.service("ALRobotPosture")
        self.animation_player = self.session.service("ALAnimationPlayer")

        self.logger.info("Created animation handler")

    def wakeup(self):
        self.motion.wakeUp()

    def reset_posture(self):
        self.posture.goToPosture("StandInit", 0.5)

    def rest(self):
        self.motion.rest()

    def set_posture(self, posture_name):
        self.posture.goToPosture("StandInit" if posture_name is None else posture_name, 0.5)

    def execute_animation(self, animation_name):
        if animation_name is None:
            self.logger.error("* Animation name was NONE...")
        try:
            self.animation_player.run(animation_name)
        except Exception as e:
            self.logger.error("* Error while trying to execute the animation: '{}' | {}".format(animation_name, e))
