# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interaction_manager/ui/importdialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from es_common.utils.qt import QtCore, QtGui, QtWidgets


class Ui_ImportBlocksDialog(object):
    def setupUi(self, ImportBlocksDialog):
        ImportBlocksDialog.setObjectName("ImportBlocksDialog")
        ImportBlocksDialog.resize(494, 431)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ImportBlocksDialog.sizePolicy().hasHeightForWidth())
        ImportBlocksDialog.setSizePolicy(sizePolicy)
        ImportBlocksDialog.setMinimumSize(QtCore.QSize(0, 0))
        ImportBlocksDialog.setMaximumSize(QtCore.QSize(1000, 800))
        self.gridLayout_3 = QtWidgets.QGridLayout(ImportBlocksDialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox = QtWidgets.QGroupBox(ImportBlocksDialog)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_12 = QtWidgets.QGridLayout()
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.portLabel = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.portLabel.setFont(font)
        self.portLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.portLabel.setObjectName("portLabel")
        self.gridLayout_12.addWidget(self.portLabel, 1, 0, 1, 1)
        self.fileNameLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.fileNameLineEdit.setObjectName("fileNameLineEdit")
        self.gridLayout_12.addWidget(self.fileNameLineEdit, 2, 0, 1, 3)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.messageTextEdit = QtWidgets.QTextEdit(self.groupBox_2)
        self.messageTextEdit.setAutoFillBackground(True)
        self.messageTextEdit.setStyleSheet("background: rgb(76, 76, 76)")
        self.messageTextEdit.setObjectName("messageTextEdit")
        self.gridLayout.addWidget(self.messageTextEdit, 0, 0, 1, 1)
        self.gridLayout_12.addWidget(self.groupBox_2, 4, 0, 1, 4)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_12.addItem(spacerItem, 7, 1, 1, 1)
        self.selectFileToolButton = QtWidgets.QToolButton(self.groupBox)
        self.selectFileToolButton.setObjectName("selectFileToolButton")
        self.gridLayout_12.addWidget(self.selectFileToolButton, 2, 3, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.groupBox)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_12.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_12.addWidget(self.line, 0, 0, 1, 4)
        self.line_2 = QtWidgets.QFrame(self.groupBox)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_12.addWidget(self.line_2, 3, 0, 1, 4)
        self.gridLayout_2.addLayout(self.gridLayout_12, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(ImportBlocksDialog)
        self.buttonBox.accepted.connect(ImportBlocksDialog.accept)
        self.buttonBox.rejected.connect(ImportBlocksDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportBlocksDialog)

    def retranslateUi(self, ImportBlocksDialog):
        _translate = QtCore.QCoreApplication.translate
        ImportBlocksDialog.setWindowTitle(_translate("ImportBlocksDialog", "Import Dialog"))
        self.groupBox.setTitle(_translate("ImportBlocksDialog", "Import Design"))
        self.portLabel.setText(_translate("ImportBlocksDialog", "Select file:"))
        self.groupBox_2.setTitle(_translate("ImportBlocksDialog", "Result"))
        self.selectFileToolButton.setText(_translate("ImportBlocksDialog", "..."))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ImportBlocksDialog = QtWidgets.QDialog()
    ui = Ui_ImportBlocksDialog()
    ui.setupUi(ImportBlocksDialog)
    ImportBlocksDialog.show()
    sys.exit(app.exec_())
