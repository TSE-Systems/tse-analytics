# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trafficage_preprocessed_data_widget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGroupBox,
    QHBoxLayout, QHeaderView, QListWidget, QListWidgetItem,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)
import resources_rc

class Ui_TraffiCagePreprocessedDataWidget(object):
    def setupUi(self, TraffiCagePreprocessedDataWidget):
        if not TraffiCagePreprocessedDataWidget.objectName():
            TraffiCagePreprocessedDataWidget.setObjectName(u"TraffiCagePreprocessedDataWidget")
        self.horizontalLayout = QHBoxLayout(TraffiCagePreprocessedDataWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxTables = QGroupBox(TraffiCagePreprocessedDataWidget)
        self.groupBoxTables.setObjectName(u"groupBoxTables")
        self.verticalLayout = QVBoxLayout(self.groupBoxTables)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidgetTables = QListWidget(self.groupBoxTables)
        self.listWidgetTables.setObjectName(u"listWidgetTables")
        self.listWidgetTables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.listWidgetTables)


        self.horizontalLayout.addWidget(self.groupBoxTables)

        self.tableView = QTableView(TraffiCagePreprocessedDataWidget)
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

        self.groupBoxAnimals = QGroupBox(TraffiCagePreprocessedDataWidget)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")
        self.listWidgetAnimals.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.retranslateUi(TraffiCagePreprocessedDataWidget)

        QMetaObject.connectSlotsByName(TraffiCagePreprocessedDataWidget)
    # setupUi

    def retranslateUi(self, TraffiCagePreprocessedDataWidget):
        self.groupBoxTables.setTitle(QCoreApplication.translate("TraffiCagePreprocessedDataWidget", u"Data Tables", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("TraffiCagePreprocessedDataWidget", u"Animals", None))
        pass
    # retranslateUi

