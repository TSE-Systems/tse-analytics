# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pca_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_PcaWidget(object):
    def setupUi(self, PcaWidget):
        if not PcaWidget.objectName():
            PcaWidget.setObjectName(u"PcaWidget")
        PcaWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(PcaWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(PcaWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.labelMethod = QLabel(PcaWidget)
        self.labelMethod.setObjectName(u"labelMethod")

        self.horizontalLayout.addWidget(self.labelMethod)

        self.comboBoxMethod = QComboBox(PcaWidget)
        self.comboBoxMethod.setObjectName(u"comboBoxMethod")

        self.horizontalLayout.addWidget(self.comboBoxMethod)

        self.labelDimensions = QLabel(PcaWidget)
        self.labelDimensions.setObjectName(u"labelDimensions")

        self.horizontalLayout.addWidget(self.labelDimensions)

        self.comboBoxDimensions = QComboBox(PcaWidget)
        self.comboBoxDimensions.setObjectName(u"comboBoxDimensions")

        self.horizontalLayout.addWidget(self.comboBoxDimensions)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(PcaWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.webView = QWebEngineView(PcaWidget)
        self.webView.setObjectName(u"webView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.webView)


        self.retranslateUi(PcaWidget)

        QMetaObject.connectSlotsByName(PcaWidget)
    # setupUi

    def retranslateUi(self, PcaWidget):
        PcaWidget.setWindowTitle(QCoreApplication.translate("PcaWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("PcaWidget", u"Analyze", None))
        self.labelMethod.setText(QCoreApplication.translate("PcaWidget", u"Method:", None))
        self.labelDimensions.setText(QCoreApplication.translate("PcaWidget", u"Dimensions:", None))
    # retranslateUi

