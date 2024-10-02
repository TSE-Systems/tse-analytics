# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'factors_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
import resources_rc

class Ui_FactorsWidget(object):
    def setupUi(self, FactorsWidget):
        if not FactorsWidget.objectName():
            FactorsWidget.setObjectName(u"FactorsWidget")
        self.verticalLayout = QVBoxLayout(FactorsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(FactorsWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setDefaultSectionSize(24)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(FactorsWidget)

        QMetaObject.connectSlotsByName(FactorsWidget)
    # setupUi

    def retranslateUi(self, FactorsWidget):
        pass
    # retranslateUi

