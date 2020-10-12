#!/usr/bin/env python3
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

from es_common.utils.qt import QtWidgets

from interaction_manager.controller.ui_controller import UIController


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("macintosh")

    win = UIController()
    win.show()
    win.repaint()
    win.update()
    if app.exec_() == 0:
        print("Exec...")
        win.exit_gracefully()
        sys.exit(0)
    # sys.exit(app.exec_())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(filename)s:%(lineno)4d: %(message)s",
                        stream=sys.stdout)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
