#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========== #
# OBSERVABLE #
# ========== #
# Observer pattern.
#
# @author ES
# **

class Observable(object):
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        if observer is not None and not (observer in self.observers):
            self.observers.append(observer)

    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
            return True

        return False

    def remove_all(self):
        self.observers = []

    def notify_all(self, event):
        for observer in self.observers:
            if observer:
                observer(event)
