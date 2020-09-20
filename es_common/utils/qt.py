# PyQt and PySide2 import helper

import logging

logger = logging.getLogger("Qt Import")

try:
    # PySide2
    from PySide2 import QtGui, QtWidgets, QtCore
    from PySide2.QtCore import Signal, QTimer
    from PySide2.QtCore import Qt, QThread, QRectF, QPointF
    from PySide2.QtCore import QSize, Qt, QByteArray, QDataStream, QIODevice, QMimeData, QPoint
    from PySide2.QtGui import QPen, QBrush, QPainter, QPainterPath, QFont
    from PySide2.QtGui import QDrag, QIcon, QPixmap, QColor
    from PySide2.QtWidgets import QApplication, QWidget, QGraphicsProxyWidget, QVBoxLayout
    from PySide2.QtWidgets import QGraphicsView, QGraphicsScene
    from PySide2.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsPathItem
    from PySide2.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QTextEdit, QLineEdit, QLabel
    from PySide2.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
except ImportError:
    logger.info("Importing PyQt5")
    # PyQt5
    # from PyQt5 import QtGui, QtWidgets, QtCore
    # from PyQt5.QtCore import pyqtSignal as Signal, QTimer
    # from PyQt5.QtCore import Qt, QThread, QRectF, QPointF
    # from PyQt5.QtCore import QSize, Qt, QByteArray, QDataStream, QIODevice, QMimeData, QPoint
    # from PyQt5.QtGui import QPen, QBrush, QPainter, QPainterPath, QFont
    # from PyQt5.QtGui import QDrag, QIcon, QPixmap, QColor
    # from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsProxyWidget, QVBoxLayout
    # from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
    # from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsPathItem
    # from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QTextEdit, QLineEdit, QLabel
    # from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
