# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'factors_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QSizePolicy, QSpacerItem, QTableView, QToolButton,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_FactorsWidget(object):
    def setupUi(self, FactorsWidget):
        if not FactorsWidget.objectName():
            FactorsWidget.setObjectName(u"FactorsWidget")
        FactorsWidget.resize(489, 630)
        self.verticalLayout = QVBoxLayout(FactorsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonEditFactors = QToolButton(FactorsWidget)
        self.toolButtonEditFactors.setObjectName(u"toolButtonEditFactors")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-edit-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonEditFactors.setIcon(icon)
        self.toolButtonEditFactors.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.toolButtonEditFactors)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tableView = QTableView(FactorsWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout.addWidget(self.tableView)


        self.retranslateUi(FactorsWidget)

        QMetaObject.connectSlotsByName(FactorsWidget)
    # setupUi

    def retranslateUi(self, FactorsWidget):
        FactorsWidget.setWindowTitle(QCoreApplication.translate("FactorsWidget", u"Form", None))
        self.toolButtonEditFactors.setText(QCoreApplication.translate("FactorsWidget", u"Edit Factors", None))
    # retranslateUi

