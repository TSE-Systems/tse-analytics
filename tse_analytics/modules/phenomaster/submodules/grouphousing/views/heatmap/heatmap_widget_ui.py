# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'heatmap_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QGroupBox, QHBoxLayout,
    QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
import resources_rc

class Ui_HeatmapWidget(object):
    def setupUi(self, HeatmapWidget):
        if not HeatmapWidget.objectName():
            HeatmapWidget.setObjectName(u"HeatmapWidget")
        self.horizontalLayout = QHBoxLayout(HeatmapWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.canvas = MplCanvas(HeatmapWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.groupBoxAnimals = QGroupBox(HeatmapWidget)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listWidgetAnimals.sizePolicy().hasHeightForWidth())
        self.listWidgetAnimals.setSizePolicy(sizePolicy1)
        self.listWidgetAnimals.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout_2.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.retranslateUi(HeatmapWidget)

        QMetaObject.connectSlotsByName(HeatmapWidget)
    # setupUi

    def retranslateUi(self, HeatmapWidget):
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("HeatmapWidget", u"Animals", None))
        pass
    # retranslateUi

