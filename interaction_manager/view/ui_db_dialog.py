# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hre_ui/ui_dialog/dbdialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from es_common.utils.qt import QtCore, QtGui, QtWidgets


class Ui_DBDialog(object):
    def setupUi(self, DBDialog):
        DBDialog.setObjectName("DBDialog")
        DBDialog.resize(474, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DBDialog.sizePolicy().hasHeightForWidth())
        DBDialog.setSizePolicy(sizePolicy)
        DBDialog.setMinimumSize(QtCore.QSize(400, 300))
        DBDialog.setMaximumSize(QtCore.QSize(500, 400))
        self.gridLayout_2 = QtWidgets.QGridLayout(DBDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(DBDialog)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_12 = QtWidgets.QGridLayout()
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setText("")
        self.label.setObjectName("label")
        self.gridLayout_12.addWidget(self.label, 5, 0, 1, 3)
        self.robotIPLabel = QtWidgets.QLabel(self.groupBox)
        self.robotIPLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.robotIPLabel.setObjectName("robotIPLabel")
        self.gridLayout_12.addWidget(self.robotIPLabel, 0, 0, 1, 1)
        self.generateNamePushButton = QtWidgets.QPushButton(self.groupBox)
        self.generateNamePushButton.setObjectName("generateNamePushButton")
        self.gridLayout_12.addWidget(self.generateNamePushButton, 2, 2, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.groupBox)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_12.addWidget(self.buttonBox, 6, 1, 1, 2)
        self.dbNameLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.dbNameLineEdit.setObjectName("dbNameLineEdit")
        self.gridLayout_12.addWidget(self.dbNameLineEdit, 2, 1, 1, 1)
        self.portLabel = QtWidgets.QLabel(self.groupBox)
        self.portLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.portLabel.setObjectName("portLabel")
        self.gridLayout_12.addWidget(self.portLabel, 2, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_12.addWidget(self.line, 1, 0, 1, 3)
        self.setDBPushButton = QtWidgets.QPushButton(self.groupBox)
        self.setDBPushButton.setObjectName("setDBPushButton")
        self.gridLayout_12.addWidget(self.setDBPushButton, 3, 1, 1, 2)
        self.dbNamesComboBox = QtWidgets.QComboBox(self.groupBox)
        self.dbNamesComboBox.setObjectName("dbNamesComboBox")
        self.gridLayout_12.addWidget(self.dbNamesComboBox, 0, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_12.addItem(spacerItem, 8, 1, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.groupBox)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_12.addWidget(self.line_2, 4, 0, 1, 3)
        self.gridLayout.addLayout(self.gridLayout_12, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(DBDialog)
        self.buttonBox.accepted.connect(DBDialog.accept)
        self.buttonBox.rejected.connect(DBDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DBDialog)

    def retranslateUi(self, DBDialog):
        _translate = QtCore.QCoreApplication.translate
        DBDialog.setWindowTitle(_translate("DBDialog", "DB Dialog"))
        self.groupBox.setTitle(_translate("DBDialog", "Mongo DB"))
        self.robotIPLabel.setText(_translate("DBDialog", "Select DB"))
        self.generateNamePushButton.setText(_translate("DBDialog", "Generate"))
        self.portLabel.setText(_translate("DBDialog", "Create new DB"))
        self.setDBPushButton.setText(_translate("DBDialog", "Set DB"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DBDialog = QtWidgets.QDialog()
    ui = Ui_DBDialog()
    ui.setupUi(DBDialog)
    DBDialog.show()
    sys.exit(app.exec_())
