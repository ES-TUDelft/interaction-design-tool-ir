#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# TABLET_PAGE #
# =========== #
# Model for the page displayed on the tablet
#
# @author ES
# **

import logging


class TabletPage(object):

    def __init__(self, name="index", heading="", text="", image=None):
        """
        heading: heading text
        text: content
        """
        self.logger = logging.getLogger("Tablet Page")

        self.name = name
        self.heading = heading
        self.text = text
        self.image = image

    def clone(self):
        return TabletPage(self.name, self.heading, self.text, self.image)

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        return {
            'name': self.name,
            'heading': self.heading,
            'text': self.text,
            'image': self.image
        }

    @staticmethod
    def create_tablet_page(page_dict):
        if page_dict:
            return TabletPage(page_dict["name"], page_dict["heading"], page_dict["text"], page_dict['image'])
        return None
