# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'glm_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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

class Ui_GlmWidget(object):
    def setupUi(self, GlmWidget):
        if not GlmWidget.objectName():
            GlmWidget.setObjectName(u"GlmWidget")
        GlmWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(GlmWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(GlmWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.labelVariableCovariate = QLabel(GlmWidget)
        self.labelVariableCovariate.setObjectName(u"labelVariableCovariate")

        self.horizontalLayout.addWidget(self.labelVariableCovariate)

        self.variableSelectorCovariate = VariableSelector(GlmWidget)
        self.variableSelectorCovariate.setObjectName(u"variableSelectorCovariate")

        self.horizontalLayout.addWidget(self.variableSelectorCovariate)

        self.labelVariableResponse = QLabel(GlmWidget)
        self.labelVariableResponse.setObjectName(u"labelVariableResponse")

        self.horizontalLayout.addWidget(self.labelVariableResponse)

        self.variableSelectorResponse = VariableSelector(GlmWidget)
        self.variableSelectorResponse.setObjectName(u"variableSelectorResponse")

        self.horizontalLayout.addWidget(self.variableSelectorResponse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(GlmWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(GlmWidget)
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


        self.retranslateUi(GlmWidget)

        QMetaObject.connectSlotsByName(GlmWidget)
    # setupUi

    def retranslateUi(self, GlmWidget):
        GlmWidget.setWindowTitle(QCoreApplication.translate("GlmWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("GlmWidget", u"Analyze", None))
        self.labelVariableCovariate.setText(QCoreApplication.translate("GlmWidget", u"Covariate:", None))
        self.labelVariableResponse.setText(QCoreApplication.translate("GlmWidget", u"Response:", None))
    # retranslateUi

