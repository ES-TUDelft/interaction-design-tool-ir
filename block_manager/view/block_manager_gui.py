# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'block_manager/ui/blockmanagergui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BlockManagerGUI(object):
    def setupUi(self, BlockManagerGUI):
        BlockManagerGUI.setObjectName("BlockManagerGUI")
        BlockManagerGUI.resize(649, 525)
        self.centralWidget = QtWidgets.QWidget(BlockManagerGUI)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout_4.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_4.setSpacing(6)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.designPanelLayout = QtWidgets.QGridLayout()
        self.designPanelLayout.setSpacing(6)
        self.designPanelLayout.setObjectName("designPanelLayout")
        self.widget = QtWidgets.QWidget(self.centralWidget)
        self.widget.setObjectName("widget")
        self.designPanelLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.designPanelLayout, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        BlockManagerGUI.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(BlockManagerGUI)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 649, 22))
        self.menuBar.setObjectName("menuBar")
        BlockManagerGUI.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(BlockManagerGUI)
        self.mainToolBar.setObjectName("mainToolBar")
        BlockManagerGUI.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(BlockManagerGUI)
        self.statusBar.setObjectName("statusBar")
        BlockManagerGUI.setStatusBar(self.statusBar)
        self.dockWidget = QtWidgets.QDockWidget(BlockManagerGUI)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.resetViewPushButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.resetViewPushButton.setObjectName("resetViewPushButton")
        self.gridLayout_2.addWidget(self.resetViewPushButton, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.dockWidget.setWidget(self.dockWidgetContents)
        BlockManagerGUI.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)

        self.retranslateUi(BlockManagerGUI)
        QtCore.QMetaObject.connectSlotsByName(BlockManagerGUI)

    def retranslateUi(self, BlockManagerGUI):
        _translate = QtCore.QCoreApplication.translate
        BlockManagerGUI.setWindowTitle(_translate("BlockManagerGUI", "NodeManagerGUI"))
        self.label.setText(_translate("BlockManagerGUI", "Design Space"))
        self.resetViewPushButton.setText(_translate("BlockManagerGUI", "Reset View"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BlockManagerGUI = QtWidgets.QMainWindow()
    ui = Ui_BlockManagerGUI()
    ui.setupUi(BlockManagerGUI)
    BlockManagerGUI.show()
    sys.exit(app.exec_())

