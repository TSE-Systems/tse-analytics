# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'raw_data_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
    QHBoxLayout, QListWidget, QListWidgetItem, QSizePolicy,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_RawDataWidget(object):
    def setupUi(self, RawDataWidget):
        if not RawDataWidget.objectName():
            RawDataWidget.setObjectName(u"RawDataWidget")
        self.horizontalLayout = QHBoxLayout(RawDataWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxData = QGroupBox(RawDataWidget)
        self.groupBoxData.setObjectName(u"groupBoxData")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxData.sizePolicy().hasHeightForWidth())
        self.groupBoxData.setSizePolicy(sizePolicy)
        self.tableLayout = QVBoxLayout(self.groupBoxData)
        self.tableLayout.setSpacing(0)
        self.tableLayout.setObjectName(u"tableLayout")
        self.tableLayout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout.addWidget(self.groupBoxData)

        self.groupBoxAnimals = QGroupBox(RawDataWidget)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")
        self.listWidgetAnimals.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.retranslateUi(RawDataWidget)

        QMetaObject.connectSlotsByName(RawDataWidget)
    # setupUi

    def retranslateUi(self, RawDataWidget):
        self.groupBoxData.setTitle(QCoreApplication.translate("RawDataWidget", u"Data", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("RawDataWidget", u"Animals", None))
        pass
    # retranslateUi

