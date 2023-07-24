# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'matrix_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QSpacerItem,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_MatrixWidget(object):
    def setupUi(self, MatrixWidget):
        if not MatrixWidget.objectName():
            MatrixWidget.setObjectName(u"MatrixWidget")
        MatrixWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(MatrixWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(MatrixWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(MatrixWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.webView = QWebEngineView(MatrixWidget)
        self.webView.setObjectName(u"webView")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.webView)


        self.retranslateUi(MatrixWidget)

        QMetaObject.connectSlotsByName(MatrixWidget)
    # setupUi

    def retranslateUi(self, MatrixWidget):
        MatrixWidget.setWindowTitle(QCoreApplication.translate("MatrixWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("MatrixWidget", u"Analyze", None))
    # retranslateUi

