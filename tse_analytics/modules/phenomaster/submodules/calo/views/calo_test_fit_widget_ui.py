# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_test_fit_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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

class Ui_CaloTestFitWidget(object):
    def setupUi(self, CaloTestFitWidget):
        if not CaloTestFitWidget.objectName():
            CaloTestFitWidget.setObjectName(u"CaloTestFitWidget")
        self.verticalLayout = QVBoxLayout(CaloTestFitWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonFit = QToolButton(CaloTestFitWidget)
        self.toolButtonFit.setObjectName(u"toolButtonFit")

        self.horizontalLayout.addWidget(self.toolButtonFit)

        self.toolButtonExport = QToolButton(CaloTestFitWidget)
        self.toolButtonExport.setObjectName(u"toolButtonExport")
        self.toolButtonExport.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        self.horizontalLayout.addWidget(self.toolButtonExport)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.labelT90 = QLabel(CaloTestFitWidget)
        self.labelT90.setObjectName(u"labelT90")

        self.horizontalLayout.addWidget(self.labelT90)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(CaloTestFitWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(CaloTestFitWidget)

        QMetaObject.connectSlotsByName(CaloTestFitWidget)
    # setupUi

    def retranslateUi(self, CaloTestFitWidget):
        CaloTestFitWidget.setWindowTitle(QCoreApplication.translate("CaloTestFitWidget", u"Form", None))
        self.toolButtonFit.setText(QCoreApplication.translate("CaloTestFitWidget", u"Calculate Test Fit", None))
        self.toolButtonExport.setText(QCoreApplication.translate("CaloTestFitWidget", u"Export", None))
    # retranslateUi

