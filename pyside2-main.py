#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======== #
# HRE_MAIN #
# ======== #
# Class for launching the main GUI
#
# @author ES
# **

import logging
import sys

from PySide2.QtWidgets import QApplication, QMainWindow

from interaction_manager.view.ui_dialog_pyside2 import Ui_DialogGUI


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_DialogGUI()
        self.ui.setupUi(self)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(filename)s:%(lineno)4d: %(message)s",
                        stream=sys.stdout)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
