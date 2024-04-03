# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'meal_details_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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

from tse_analytics.modules.phenomaster.meal_details.views.meal_details_plot_view import MealDetailsPlotView
from tse_analytics.views.misc.variable_selector import VariableSelector

class Ui_MealDetailsPlotWidget(object):
    def setupUi(self, MealDetailsPlotWidget):
        if not MealDetailsPlotWidget.objectName():
            MealDetailsPlotWidget.setObjectName(u"MealDetailsPlotWidget")
        MealDetailsPlotWidget.resize(538, 607)
        self.verticalLayout = QVBoxLayout(MealDetailsPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(MealDetailsPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(MealDetailsPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.plotView = MealDetailsPlotView(MealDetailsPlotWidget)
        self.plotView.setObjectName(u"plotView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotView.sizePolicy().hasHeightForWidth())
        self.plotView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.plotView)


        self.retranslateUi(MealDetailsPlotWidget)

        QMetaObject.connectSlotsByName(MealDetailsPlotWidget)
    # setupUi

    def retranslateUi(self, MealDetailsPlotWidget):
        MealDetailsPlotWidget.setWindowTitle(QCoreApplication.translate("MealDetailsPlotWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("MealDetailsPlotWidget", u"Variable:", None))
    # retranslateUi

