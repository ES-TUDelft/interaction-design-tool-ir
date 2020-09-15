#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# TIMER_THREAD #
# ============ #
# Threads for timing events
#
# @author ES
# **

import logging
import time
from timeit import default_timer as timer

from PyQt5.QtCore import QThread, pyqtSignal

"""
TIMER THREAD
"""


class TimerThread(QThread):
    time_is_up_signal = pyqtSignal(bool)

    def __init__(self):
        QThread.__init__(self)
        self.logger = logging.getLogger("TimerThread")
        self.max_time = 0
        self.starting_time = 0
        self.stop_timer = False

    def __del__(self):
        self.wait()

    def stop_running(self):
        self.stop_timer = True

    def start_timer(self):
        if not self.isRunning():
            self.logger.info("Started the timer.")
            self.start()

    def run(self):
        self.starting_time = timer()
        self.stop_timer = False

        while not self.stop_timer:
            if self.max_time > 0 and (timer() - self.starting_time > self.max_time):
                self.logger.info("TIME IS UP ({})".format(timer() - self.starting_time))
                self.time_is_up_signal.emit(True)  # emit a signal every 10s until the timer is stopped
            time.sleep(10)
        self.logger.info("Stopped the timer.")
