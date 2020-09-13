#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ================== #
# HISTORY_CONTROLLER #
# ================== #
# Abstract class for tracking the history.
#
# @author ES
# **

import logging
from block_manager.utils import config_helper


class HistoryController(object):
    def __init__(self):

        self.logger = logging.getLogger("HistoryController")

        self.history_stack = []

        self.current_step = -1
        self.step_limit = config_helper.get_history_limit()

    def store(self, description):
        """
        Stores current state in stack
        :param description: string description of stamp
        """
        success = False
        try:
            h_stamp = self.create_stamp(description)
            if h_stamp is None:
                self.logger.error("Couldn't create a snapshot of the scene!")
            else:
                next_step = self.current_step + 1

                # if current step is not at the end of the history
                if next_step < len(self.history_stack):
                    # shrink stack
                    self.history_stack = self.history_stack[0:next_step]
                elif next_step >= self.step_limit:  # next step is off limits
                    # remove first element
                    self.history_stack = self.history_stack[1:]
                    self.current_step -= 1

                self.history_stack.append(h_stamp)
                self.current_step += 1

                self.logger.debug("Storing at {}".format(self.current_step))
                success = True
        except Exception as e:
            self.logger.error("Error while storing the scene! {}".format(e))
        finally:
            return success

    def restore(self):
        """
        Restores history from stack
        """
        self.restore_stamp(self.history_stack[self.current_step])

    def can_undo(self):
        return self.current_step > 0

    def can_redo(self):
        return self.current_step + 1 < len(self.history_stack)

    def undo(self):
        self.logger.debug("Undo {}".format(self.current_step))
        if self.can_undo():
            self.current_step -= 1
            self.restore()

    def redo(self):
        self.logger.debug("Redo {}".format(self.current_step))
        if self.can_redo():
            self.current_step += 1
            self.restore()

    def clear(self):
        """
        Clears history stack and current step
        """
        self.history_stack = []
        self.current_step = -1

    def create_stamp(self, description):
        """
        serialize history

        :param description:
        :return: history_stamp
        """
        raise NotImplemented

    def restore_stamp(self, stamp):
        """
        restore history from stamp

        :param stamp:
        :return:
        """
        raise NotImplemented
