# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'anova_widget.ui'
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QSplitter, QToolButton, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_AnovaWidget(object):
    def setupUi(self, AnovaWidget):
        if not AnovaWidget.objectName():
            AnovaWidget.setObjectName(u"AnovaWidget")
        AnovaWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(AnovaWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(AnovaWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.labelVariable = QLabel(AnovaWidget)
        self.labelVariable.setObjectName(u"labelVariable")

        self.horizontalLayout.addWidget(self.labelVariable)

        self.variableSelector = VariableSelector(AnovaWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(AnovaWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(AnovaWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Vertical)
        self.canvas = MplCanvas(self.splitter)
        self.canvas.setObjectName(u"canvas")
        self.splitter.addWidget(self.canvas)
        self.webView = QWebEngineView(self.splitter)
        self.webView.setObjectName(u"webView")
        self.splitter.addWidget(self.webView)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(AnovaWidget)

        QMetaObject.connectSlotsByName(AnovaWidget)
    # setupUi

    def retranslateUi(self, AnovaWidget):
        AnovaWidget.setWindowTitle(QCoreApplication.translate("AnovaWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("AnovaWidget", u"Analyze", None))
        self.labelVariable.setText(QCoreApplication.translate("AnovaWidget", u"Variable:", None))
    # retranslateUi

