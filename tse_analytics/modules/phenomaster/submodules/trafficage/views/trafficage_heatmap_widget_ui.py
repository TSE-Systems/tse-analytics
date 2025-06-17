# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trafficage_heatmap_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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

from tse_analytics.views.misc.MplCanvas import MplCanvas
import resources_rc

class Ui_TraffiCageHeatmapWidget(object):
    def setupUi(self, TraffiCageHeatmapWidget):
        if not TraffiCageHeatmapWidget.objectName():
            TraffiCageHeatmapWidget.setObjectName(u"TraffiCageHeatmapWidget")
        self.horizontalLayout = QHBoxLayout(TraffiCageHeatmapWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.canvas = MplCanvas(TraffiCageHeatmapWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.canvas)

        self.groupBoxAnimals = QGroupBox(TraffiCageHeatmapWidget)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")
        self.listWidgetAnimals.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.listWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout_2.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.retranslateUi(TraffiCageHeatmapWidget)

        QMetaObject.connectSlotsByName(TraffiCageHeatmapWidget)
    # setupUi

    def retranslateUi(self, TraffiCageHeatmapWidget):
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("TraffiCageHeatmapWidget", u"Animals", None))
        pass
    # retranslateUi

