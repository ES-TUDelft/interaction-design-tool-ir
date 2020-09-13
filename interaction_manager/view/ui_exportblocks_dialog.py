# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interaction_manager/ui/exportdialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExportBlocksDialog(object):
    def setupUi(self, ExportBlocksDialog):
        ExportBlocksDialog.setObjectName("ExportBlocksDialog")
        ExportBlocksDialog.resize(513, 451)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ExportBlocksDialog.sizePolicy().hasHeightForWidth())
        ExportBlocksDialog.setSizePolicy(sizePolicy)
        ExportBlocksDialog.setMinimumSize(QtCore.QSize(0, 0))
        ExportBlocksDialog.setMaximumSize(QtCore.QSize(1000, 800))
        self.gridLayout_3 = QtWidgets.QGridLayout(ExportBlocksDialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox = QtWidgets.QGroupBox(ExportBlocksDialog)
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
        self.fileNameLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.fileNameLineEdit.setObjectName("fileNameLineEdit")
        self.gridLayout_12.addWidget(self.fileNameLineEdit, 3, 0, 1, 4)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_12.addWidget(self.line, 0, 0, 1, 4)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_12.addItem(spacerItem, 9, 1, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.groupBox)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_12.addWidget(self.line_2, 5, 0, 1, 4)
        self.exportBlocksButton = QtWidgets.QPushButton(self.groupBox)
        self.exportBlocksButton.setObjectName("exportBlocksButton")
        self.gridLayout_12.addWidget(self.exportBlocksButton, 4, 1, 1, 3)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.messageTextEdit = QtWidgets.QTextEdit(self.groupBox_2)
        self.messageTextEdit.setAutoFillBackground(True)
        self.messageTextEdit.setStyleSheet("background: rgb(76, 76, 76)")
        self.messageTextEdit.setObjectName("messageTextEdit")
        self.gridLayout.addWidget(self.messageTextEdit, 0, 0, 1, 1)
        self.gridLayout_12.addWidget(self.groupBox_2, 6, 0, 1, 4)
        self.selectFolderToolButton = QtWidgets.QToolButton(self.groupBox)
        self.selectFolderToolButton.setObjectName("selectFolderToolButton")
        self.gridLayout_12.addWidget(self.selectFolderToolButton, 1, 3, 1, 1)
        self.folderNameLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.folderNameLineEdit.setObjectName("folderNameLineEdit")
        self.gridLayout_12.addWidget(self.folderNameLineEdit, 1, 0, 1, 3)
        self.label = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(12)
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout_12.addWidget(self.label, 2, 0, 1, 4)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.groupBox)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_12.addWidget(self.buttonBox, 7, 0, 1, 4)
        self.gridLayout_2.addLayout(self.gridLayout_12, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(ExportBlocksDialog)
        self.buttonBox.accepted.connect(ExportBlocksDialog.accept)
        self.buttonBox.rejected.connect(ExportBlocksDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExportBlocksDialog)

    def retranslateUi(self, ExportBlocksDialog):
        _translate = QtCore.QCoreApplication.translate
        ExportBlocksDialog.setWindowTitle(_translate("ExportBlocksDialog", "Export Dialog"))
        self.groupBox.setTitle(_translate("ExportBlocksDialog", "Export Design"))
        self.fileNameLineEdit.setPlaceholderText(_translate("ExportBlocksDialog", "File Name"))
        self.exportBlocksButton.setText(_translate("ExportBlocksDialog", "Export"))
        self.groupBox_2.setTitle(_translate("ExportBlocksDialog", "Result"))
        self.selectFolderToolButton.setText(_translate("ExportBlocksDialog", "..."))
        self.folderNameLineEdit.setPlaceholderText(_translate("ExportBlocksDialog", "Select Folder"))
        self.label.setText(_translate("ExportBlocksDialog", "Note: if the file exists, it will be overwritten!"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ExportBlocksDialog = QtWidgets.QDialog()
    ui = Ui_ExportBlocksDialog()
    ui.setupUi(ExportBlocksDialog)
    ExportBlocksDialog.show()
    sys.exit(app.exec_())
