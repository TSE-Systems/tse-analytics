# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'correlation_widget.ui'
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QSplitter, QToolButton, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_CorrelationWidget(object):
    def setupUi(self, CorrelationWidget):
        if not CorrelationWidget.objectName():
            CorrelationWidget.setObjectName(u"CorrelationWidget")
        CorrelationWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(CorrelationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(CorrelationWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.labelVariableX = QLabel(CorrelationWidget)
        self.labelVariableX.setObjectName(u"labelVariableX")

        self.horizontalLayout.addWidget(self.labelVariableX)

        self.variableSelectorX = VariableSelector(CorrelationWidget)
        self.variableSelectorX.setObjectName(u"variableSelectorX")

        self.horizontalLayout.addWidget(self.variableSelectorX)

        self.labelVariableY = QLabel(CorrelationWidget)
        self.labelVariableY.setObjectName(u"labelVariableY")

        self.horizontalLayout.addWidget(self.labelVariableY)

        self.variableSelectorY = VariableSelector(CorrelationWidget)
        self.variableSelectorY.setObjectName(u"variableSelectorY")

        self.horizontalLayout.addWidget(self.variableSelectorY)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(CorrelationWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(CorrelationWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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


        self.retranslateUi(CorrelationWidget)

        QMetaObject.connectSlotsByName(CorrelationWidget)
    # setupUi

    def retranslateUi(self, CorrelationWidget):
        CorrelationWidget.setWindowTitle(QCoreApplication.translate("CorrelationWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("CorrelationWidget", u"Analyze", None))
        self.labelVariableX.setText(QCoreApplication.translate("CorrelationWidget", u"X:", None))
        self.labelVariableY.setText(QCoreApplication.translate("CorrelationWidget", u"Y:", None))
    # retranslateUi

