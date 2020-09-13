import logging
from collections import OrderedDict

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from block_manager.utils import config_helper
from es_common.datasource.serializable import Serializable


class ESBlockContentWidget(QWidget, Serializable ):
    def __init__(self, block, parent=None):
        super(ESBlockContentWidget, self).__init__(parent=parent)
        Serializable.__init__(self)

        self.logger = logging.getLogger("BlockContent")

        self.block = block
        self.icon_dimensions = config_helper.get_block_size_settings()["icon_dim"]

        self._init_ui()

    def _init_ui(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # add block attribute
        self.layout.block = self.block
        self.setLayout(self.layout)

        self.desc_line_edit = ESQLineEdit("")
        self.desc_line_edit.setPlaceholderText("Description")
        self.desc_line_edit.setFrame(False)
        self.desc_line_edit.textEdited.connect(self.store_changes)
        # add at row 0
        self.layout.addWidget(self.desc_line_edit, 0, 0, 1, 3)

        # self.description_label = QLabel("")
        # self.layout.addWidget(self.description_label)

        # h_layout = QHBoxLayout(self)

        # edit_parameters label
        self.editing_icon = self.create_label(image_path=config_helper.get_icons()["edit"],
                                              alignment=Qt.AlignLeft)
        self.editing_icon.clicked.connect(self.open_parameters)
        # row 1, col 0
        self.layout.addWidget(self.editing_icon, 1, 0, 1, 1)

        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer_item.block = self.block
        # row 1, col 1
        # h_layout.addSpacerItem(spacer_item, 1, 1)
        self.settings_icon = self.create_label(image_path=config_helper.get_icons()["settings"],
                                               alignment=Qt.AlignRight)
        self.settings_icon.clicked.connect(self.open_settings)
        # row 1, col 2
        self.layout.addWidget(self.settings_icon, 1, 2, 1, 1)

        # self.layout.addLayout(h_layout, 1, 0)

        # self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        # self.text_edit = ESQTextEdit("Text edit")
        # self.layout.addWidget(self.text_edit)

    def create_label(self, image_path, alignment):
        icon = ESQLabel(image_path, *self.icon_dimensions, parent=self)
        icon.block = self.block
        icon.setGeometry(*(self.icon_dimensions + self.icon_dimensions))  # we need 4 parameters
        icon.setAlignment(alignment)

        return icon

    def store_changes(self, event):
        self.block.scene.store("Block Description changed")

    def open_settings(self, event):
        self.logger.info("*** settings dialog is open!")

    def open_parameters(self, event):
        self.logger.info("*** parameters dialog is open!")

    def clear_selection(self):
        self.block.scene.clear_selection()

    @property
    def description(self):
        return "{}".format(self.desc_line_edit.text())

    @description.setter
    def description(self, desc):
        self.desc_line_edit.setText(desc)

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("block", self.block.id),
            ("description", self.description)
        ])

    def deserialize(self, data, hashmap=[]):
        self.id = data["id"]
        hashmap["id"] = self

        self.block = hashmap[data["block"]]
        self.desc_line_edit.setText(data["description"])

        return True


class ESQLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        super(ESQLineEdit, self).keyPressEvent(event)

    def focusInEvent(self, event):
        self.parentWidget().clear_selection()
        super(ESQLineEdit, self).focusInEvent(event)

    def focusOutEvent(self, event):
        super(ESQLineEdit, self).focusOutEvent(event)


class ESQTextEdit(QTextEdit):
    def keyPressEvent(self, event):
        super(ESQTextEdit, self).keyPressEvent(event)

    def focusInEvent(self, event):
        self.parentWidget().clear_selection()
        super(ESQTextEdit, self).focusInEvent(event)

    def focusOutEvent(self, event):
        super(ESQTextEdit, self).focusOutEvent(event)


class ESQLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, image_path, width, height, parent=None):
        super(ESQLabel, self).__init__(parent)

        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())
        self.setObjectName("QLabel")

    def mousePressEvent(self, event):
        # p = self.parent()
        self.clicked.emit(self.objectName())
        super(ESQLabel, self).mousePressEvent(event)
