# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_details_plot_widget.ui'
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

from tse_analytics.modules.phenomaster.calo_details.views.calo_details_plot_view import CaloDetailsPlotView
from tse_analytics.views.misc.variable_selector import VariableSelector

class Ui_CaloDetailsPlotWidget(object):
    def setupUi(self, CaloDetailsPlotWidget):
        if not CaloDetailsPlotWidget.objectName():
            CaloDetailsPlotWidget.setObjectName(u"CaloDetailsPlotWidget")
        CaloDetailsPlotWidget.resize(538, 607)
        self.verticalLayout = QVBoxLayout(CaloDetailsPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(CaloDetailsPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(CaloDetailsPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.plotView = CaloDetailsPlotView(CaloDetailsPlotWidget)
        self.plotView.setObjectName(u"plotView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotView.sizePolicy().hasHeightForWidth())
        self.plotView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.plotView)


        self.retranslateUi(CaloDetailsPlotWidget)

        QMetaObject.connectSlotsByName(CaloDetailsPlotWidget)
    # setupUi

    def retranslateUi(self, CaloDetailsPlotWidget):
        CaloDetailsPlotWidget.setWindowTitle(QCoreApplication.translate("CaloDetailsPlotWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("CaloDetailsPlotWidget", u"Variable:", None))
    # retranslateUi

