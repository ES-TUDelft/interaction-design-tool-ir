#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================= #
# GRAPH_WIDGET_CONTROLLER #
# ======================= #
# Graph controller
#   Adds a graph widget to the parent widget
#
# @author ES
# **
import datetime

import pyqtgraph


class GraphWidgetController:

    def __init__(self, plot_widget):
        self.plot_widget = plot_widget

        self.axis_size = 20

        self.x_axis = [datetime.datetime.now().timestamp()] * self.axis_size
        self.y_axis = [0] * self.axis_size

        self.plot_widget.setAxisItems({"bottom": pyqtgraph.DateAxisItem()})
        label_styles = {"color": "white", "font-size": "14px"}
        self.plot_widget.setLabel("left", "Face Size", **label_styles)
        # self.plot_widget.setLabel("bottom", "Time (timestamp)", **label_styles)
        self.data_plot = self.plot_widget.plot(self.x_axis, self.y_axis, symbol="+")

    def append_data(self, value):
        if len(self.x_axis) > self.axis_size:
            self.x_axis = self.x_axis[1:]
            self.y_axis = self.y_axis[1:]

        self.x_axis.append(datetime.datetime.now().timestamp())
        self.y_axis.append(value)

        self.data_plot.setData(self.x_axis, self.y_axis)
