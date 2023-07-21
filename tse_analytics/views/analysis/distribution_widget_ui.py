# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'distribution_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_DistributionWidget(object):
    def setupUi(self, DistributionWidget):
        if not DistributionWidget.objectName():
            DistributionWidget.setObjectName(u"DistributionWidget")
        DistributionWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(DistributionWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(DistributionWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.labelVariable = QLabel(DistributionWidget)
        self.labelVariable.setObjectName(u"labelVariable")

        self.horizontalLayout.addWidget(self.labelVariable)

        self.variableSelector = VariableSelector(DistributionWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(DistributionWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(DistributionWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(DistributionWidget)

        QMetaObject.connectSlotsByName(DistributionWidget)
    # setupUi

    def retranslateUi(self, DistributionWidget):
        DistributionWidget.setWindowTitle(QCoreApplication.translate("DistributionWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("DistributionWidget", u"Analyze", None))
        self.labelVariable.setText(QCoreApplication.translate("DistributionWidget", u"Variable:", None))
    # retranslateUi

