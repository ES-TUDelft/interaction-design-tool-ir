#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================== #
# INTERACTION_DESIGN #
# ================== #
# Model for the interaction design
#
# @author ES
# **

import time


class InteractionDesign(object):
    def __init__(self, communication_style=None, blocks=None):
        self.time = time.time()
        self.communication_style = "" if communication_style is None else communication_style
        self.blocks = {} if blocks is None else blocks
        self.face_size = []

    @property
    def to_dict(self):
        block_dict = {
            'time': self.time,
            'communication_style': self.communication_style,
            'blocks': self.blocks,
            'face_size': self.face_size
        }

        return block_dict

    @staticmethod
    def create_interaction_design(design_dict):
        design = InteractionDesign()
        if design_dict:
            design.time = design_dict['time']
            design.communication_style = design_dict['communication_style']
            design.blocks = design_dict['blocks']
            design.face_size = design_dict['face_size'] if "face_size" in design_dict.keys() else []

        return design
