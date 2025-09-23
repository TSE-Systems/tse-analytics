# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'drinkfeed_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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

from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_plot_view import DrinkFeedPlotView
from tse_analytics.views.misc.variable_selector import VariableSelector

class Ui_DrinkFeedPlotWidget(object):
    def setupUi(self, DrinkFeedPlotWidget):
        if not DrinkFeedPlotWidget.objectName():
            DrinkFeedPlotWidget.setObjectName(u"DrinkFeedPlotWidget")
        DrinkFeedPlotWidget.resize(1074, 748)
        self.verticalLayout = QVBoxLayout(DrinkFeedPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(DrinkFeedPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(DrinkFeedPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.plotView = DrinkFeedPlotView(DrinkFeedPlotWidget)
        self.plotView.setObjectName(u"plotView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotView.sizePolicy().hasHeightForWidth())
        self.plotView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.plotView)


        self.retranslateUi(DrinkFeedPlotWidget)

        QMetaObject.connectSlotsByName(DrinkFeedPlotWidget)
    # setupUi

    def retranslateUi(self, DrinkFeedPlotWidget):
        DrinkFeedPlotWidget.setWindowTitle(QCoreApplication.translate("DrinkFeedPlotWidget", u"DrinkFeed", None))
        self.label.setText(QCoreApplication.translate("DrinkFeedPlotWidget", u"Variable:", None))
    # retranslateUi

