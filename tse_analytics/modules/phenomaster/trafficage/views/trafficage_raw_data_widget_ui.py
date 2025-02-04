# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trafficage_raw_data_widget.ui'
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

class Ui_TraffiCageRawDataWidget(object):
    def setupUi(self, TraffiCageRawDataWidget):
        if not TraffiCageRawDataWidget.objectName():
            TraffiCageRawDataWidget.setObjectName(u"TraffiCageRawDataWidget")
        self.horizontalLayout = QHBoxLayout(TraffiCageRawDataWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxTables = QGroupBox(TraffiCageRawDataWidget)
        self.groupBoxTables.setObjectName(u"groupBoxTables")
        self.verticalLayout = QVBoxLayout(self.groupBoxTables)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidgetTables = QListWidget(self.groupBoxTables)
        self.listWidgetTables.setObjectName(u"listWidgetTables")
        self.listWidgetTables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.listWidgetTables)


        self.horizontalLayout.addWidget(self.groupBoxTables)

        self.tableView = QTableView(TraffiCageRawDataWidget)
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

        self.groupBoxBoxes = QGroupBox(TraffiCageRawDataWidget)
        self.groupBoxBoxes.setObjectName(u"groupBoxBoxes")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxBoxes)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetBoxes = QListWidget(self.groupBoxBoxes)
        self.listWidgetBoxes.setObjectName(u"listWidgetBoxes")
        self.listWidgetBoxes.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetBoxes.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetBoxes)


        self.horizontalLayout.addWidget(self.groupBoxBoxes)


        self.retranslateUi(TraffiCageRawDataWidget)

        QMetaObject.connectSlotsByName(TraffiCageRawDataWidget)
    # setupUi

    def retranslateUi(self, TraffiCageRawDataWidget):
        self.groupBoxTables.setTitle(QCoreApplication.translate("TraffiCageRawDataWidget", u"Data Tables", None))
        self.groupBoxBoxes.setTitle(QCoreApplication.translate("TraffiCageRawDataWidget", u"Boxes", None))
        pass
    # retranslateUi

