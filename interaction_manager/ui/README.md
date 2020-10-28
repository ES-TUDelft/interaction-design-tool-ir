cd ~/path-to/robot-interaction-tool
# PyQt5
pyrcc5 interaction_manager/ui/hre_resources/resources.qrc -o interaction_manager/view/resources_rc.py;
pyuic5 -x interaction_manager/ui/dialogmainwindow.ui -o interaction_manager/view/ui_dialog.py;

pyuic5 -x interaction_manager/ui/editblockdialog.ui -o interaction_manager/view/ui_editblock_dialog.py;
pyuic5 -x interaction_manager/ui/connectiondialog.ui -o interaction_manager/view/ui_connection_dialog.py;
pyuic5 -x interaction_manager/ui/editblockdialog.ui -o interaction_manager/view/ui_editblock_dialog.py;
pyuic5 -x interaction_manager/ui/confirmationdialog.ui -o interaction_manager/view/ui_confirmation_dialog.py;
pyuic5 -x interaction_manager/ui/dbconnectiondialog.ui -o interaction_manager/view/ui_db_connection_dialog.py;
pyuic5 -x interaction_manager/ui/exportdialog.ui -o interaction_manager/view/ui_exportblocks_dialog.py;
pyuic5 -x interaction_manager/ui/importdialog.ui -o interaction_manager/view/ui_importblocks_dialog.py;
pyuic5 -x interaction_manager/ui/spotifydialog.ui -o interaction_manager/view/ui_spotify_dialog.py;
pyuic5 -x interaction_manager/ui/parametersdialog.ui -o interaction_manager/view/ui_parameters_dialog.py;
pyuic5 -x interaction_manager/ui/saveasdialog.ui -o interaction_manager/view/ui_saveas_dialog.py;

# PySide2
pyside2-rcc interaction_manager/ui/hre_resources/resources.qrc -o interaction_manager/view/resources_rc.py
pyside2-uic interaction_manager/ui/dialogmainwindow.ui -o interaction_manager/view/ui_dialog.py

