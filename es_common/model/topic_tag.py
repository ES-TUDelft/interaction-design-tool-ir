#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# TOPIC_TAG #
# =========== #
# Model for topic tags in QiChat dialogue
#
# @author ES
# **

import logging
from copy import copy


class TopicTag(object):

    def __init__(self, name="", topic="", answers=[], feedbacks=[], goto_ids=[]):

        self.logger = logging.getLogger("TopicTag")

        self.name = name
        self.topic = topic
        self.answers = answers
        self.feedbacks = feedbacks
        self.goto_ids = goto_ids

    def get_combined_answers(self):
        return join_array(self.answers)

    def clone(self):
        return TopicTag(self.name, self.topic, copy(self.answers), copy(self.feedbacks))

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        return {
            "name": self.name,
            "topic": self.topic,
            "answers": self.answers,
            "feedbacks": self.feedbacks,
            "goto_ids": self.goto_ids
        }

    @staticmethod
    def create_topic_tag(tag_dict):
        topic_tag = None

        if tag_dict:
            topic_tag = TopicTag()
            topic_tag.name = tag_dict["name"]
            topic_tag.topic = tag_dict["topic"]
            if "answers" in tag_dict.keys():
                topic_tag.answers = tag_dict["answers"]
            if "feedbacks" in tag_dict.keys():
                topic_tag.feedbacks = tag_dict["feedbacks"]
            if "goto_ids" in tag_dict.keys():
                topic_tag.goto_ids = tag_dict["goto_ids"]

        return topic_tag


# HELPER METHOD
# =============
def join_array(arr, to_split=";"):
    if arr is None or len(arr) == 0:
        return []

    result = []
    for i in range(len(arr)):
        keywords = [s.strip() for s in arr[i].split(to_split)]
        result.extend(keywords)
    # print("Result from join: {}".format(result))
    return result
