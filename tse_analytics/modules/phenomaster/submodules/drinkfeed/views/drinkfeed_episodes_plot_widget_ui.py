# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'drinkfeed_episodes_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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

class Ui_DrinkFeedEpisodesPlotWidget(object):
    def setupUi(self, DrinkFeedEpisodesPlotWidget):
        if not DrinkFeedEpisodesPlotWidget.objectName():
            DrinkFeedEpisodesPlotWidget.setObjectName(u"DrinkFeedEpisodesPlotWidget")
        self.verticalLayout = QVBoxLayout(DrinkFeedEpisodesPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(DrinkFeedEpisodesPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(DrinkFeedEpisodesPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(DrinkFeedEpisodesPlotWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(DrinkFeedEpisodesPlotWidget)

        QMetaObject.connectSlotsByName(DrinkFeedEpisodesPlotWidget)
    # setupUi

    def retranslateUi(self, DrinkFeedEpisodesPlotWidget):
        DrinkFeedEpisodesPlotWidget.setWindowTitle(QCoreApplication.translate("DrinkFeedEpisodesPlotWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("DrinkFeedEpisodesPlotWidget", u"Sensor:", None))
    # retranslateUi

