# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'variables_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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

class Ui_VariablesWidget(object):
    def setupUi(self, VariablesWidget):
        if not VariablesWidget.objectName():
            VariablesWidget.setObjectName(u"VariablesWidget")
        self.verticalLayout = QVBoxLayout(VariablesWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(VariablesWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(VariablesWidget)

        QMetaObject.connectSlotsByName(VariablesWidget)
    # setupUi

    def retranslateUi(self, VariablesWidget):
        pass
    # retranslateUi

