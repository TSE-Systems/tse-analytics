# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'animals_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QSizePolicy,
    QTableView, QVBoxLayout, QWidget)

class Ui_AnimalsWidget(object):
    def setupUi(self, AnimalsWidget):
        if not AnimalsWidget.objectName():
            AnimalsWidget.setObjectName(u"AnimalsWidget")
        AnimalsWidget.resize(489, 630)
        self.verticalLayout = QVBoxLayout(AnimalsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableView = QTableView(AnimalsWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(AnimalsWidget)

        QMetaObject.connectSlotsByName(AnimalsWidget)
    # setupUi

    def retranslateUi(self, AnimalsWidget):
        AnimalsWidget.setWindowTitle(QCoreApplication.translate("AnimalsWidget", u"Form", None))
    # retranslateUi

