# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'intellicage_preprocessed_data_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGroupBox,
    QHBoxLayout, QHeaderView, QListWidget, QListWidgetItem,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)
import resources_rc

class Ui_IntelliCagePreprocessedDataWidget(object):
    def setupUi(self, IntelliCagePreprocessedDataWidget):
        if not IntelliCagePreprocessedDataWidget.objectName():
            IntelliCagePreprocessedDataWidget.setObjectName(u"IntelliCagePreprocessedDataWidget")
        self.horizontalLayout = QHBoxLayout(IntelliCagePreprocessedDataWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxTables = QGroupBox(IntelliCagePreprocessedDataWidget)
        self.groupBoxTables.setObjectName(u"groupBoxTables")
        self.verticalLayout = QVBoxLayout(self.groupBoxTables)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidgetTables = QListWidget(self.groupBoxTables)
        self.listWidgetTables.setObjectName(u"listWidgetTables")
        self.listWidgetTables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.listWidgetTables)


        self.horizontalLayout.addWidget(self.groupBoxTables)

        self.tableView = QTableView(IntelliCagePreprocessedDataWidget)
        self.tableView.setObjectName(u"tableView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self.horizontalLayout.addWidget(self.tableView)

        self.groupBoxAnimals = QGroupBox(IntelliCagePreprocessedDataWidget)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")
        self.listWidgetAnimals.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.retranslateUi(IntelliCagePreprocessedDataWidget)

        QMetaObject.connectSlotsByName(IntelliCagePreprocessedDataWidget)
    # setupUi

    def retranslateUi(self, IntelliCagePreprocessedDataWidget):
        self.groupBoxTables.setTitle(QCoreApplication.translate("IntelliCagePreprocessedDataWidget", u"Data Tables", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("IntelliCagePreprocessedDataWidget", u"Animals", None))
        pass
    # retranslateUi

