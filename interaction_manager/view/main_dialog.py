from PyQt5 import QtWidgets

from interaction_manager.view.ui_dialog import Ui_DialogGUI

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogGUI = QtWidgets.QMainWindow()
    ui = Ui_DialogGUI()
    ui.setupUi(DialogGUI)
    DialogGUI.show()
    sys.exit(app.exec_())