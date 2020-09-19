# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interaction_manager/ui/confirmationdialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from es_common.utils.qt import QtCore, QtGui, QtWidgets

class Ui_ConfirmationDialog(object):
    def setupUi(self, ConfirmationDialog):
        ConfirmationDialog.setObjectName("ConfirmationDialog")
        ConfirmationDialog.resize(400, 292)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConfirmationDialog.sizePolicy().hasHeightForWidth())
        ConfirmationDialog.setSizePolicy(sizePolicy)
        ConfirmationDialog.setMinimumSize(QtCore.QSize(0, 0))
        ConfirmationDialog.setMaximumSize(QtCore.QSize(700, 500))
        self.gridLayout = QtWidgets.QGridLayout(ConfirmationDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.line_2 = QtWidgets.QFrame(ConfirmationDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_2.addWidget(self.line_2, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(ConfirmationDialog)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ConfirmationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.line = QtWidgets.QFrame(ConfirmationDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 3, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(ConfirmationDialog)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.confirmationTextEdit = QtWidgets.QTextEdit(self.groupBox)
        self.confirmationTextEdit.setAutoFillBackground(True)
        self.confirmationTextEdit.setUndoRedoEnabled(False)
        self.confirmationTextEdit.setAcceptRichText(False)
        self.confirmationTextEdit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.confirmationTextEdit.setObjectName("confirmationTextEdit")
        self.gridLayout_3.addWidget(self.confirmationTextEdit, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(ConfirmationDialog)
        self.buttonBox.accepted.connect(ConfirmationDialog.accept)
        self.buttonBox.rejected.connect(ConfirmationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfirmationDialog)

    def retranslateUi(self, ConfirmationDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfirmationDialog.setWindowTitle(_translate("ConfirmationDialog", "Confirm Action"))
        self.label.setText(_translate("ConfirmationDialog", "Are you sure?"))
        self.groupBox.setTitle(_translate("ConfirmationDialog", "Warning"))
        self.confirmationTextEdit.setHtml(_translate("ConfirmationDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Courier New\'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'.SF NS Text\'; font-size:13pt; font-style:italic;\">All items will be deleted!</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfirmationDialog = QtWidgets.QDialog()
    ui = Ui_ConfirmationDialog()
    ui.setupUi(ConfirmationDialog)
    ConfirmationDialog.show()
    sys.exit(app.exec_())

