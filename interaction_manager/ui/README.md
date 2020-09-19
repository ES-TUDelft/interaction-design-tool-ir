cd ~/path-to/robot-interaction-tool
pyrcc5 -o interaction_manager/view/resources_rc.py interaction_manager/ui/hre_resources/resources.qrc;
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



