# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'meal_episodes_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector

class Ui_MealEpisodesPlotWidget(object):
    def setupUi(self, MealEpisodesPlotWidget):
        if not MealEpisodesPlotWidget.objectName():
            MealEpisodesPlotWidget.setObjectName(u"MealEpisodesPlotWidget")
        MealEpisodesPlotWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(MealEpisodesPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(MealEpisodesPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(MealEpisodesPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(MealEpisodesPlotWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(MealEpisodesPlotWidget)

        QMetaObject.connectSlotsByName(MealEpisodesPlotWidget)
    # setupUi

    def retranslateUi(self, MealEpisodesPlotWidget):
        MealEpisodesPlotWidget.setWindowTitle(QCoreApplication.translate("MealEpisodesPlotWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("MealEpisodesPlotWidget", u"Sensor:", None))
    # retranslateUi

