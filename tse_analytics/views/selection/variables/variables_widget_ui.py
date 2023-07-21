# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'variables_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
        VariablesWidget.resize(489, 630)
        self.verticalLayout = QVBoxLayout(VariablesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableView = QTableView(VariablesWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(VariablesWidget)

        QMetaObject.connectSlotsByName(VariablesWidget)
    # setupUi

    def retranslateUi(self, VariablesWidget):
        VariablesWidget.setWindowTitle(QCoreApplication.translate("VariablesWidget", u"Form", None))
    # retranslateUi

