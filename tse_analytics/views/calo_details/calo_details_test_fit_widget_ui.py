# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_details_test_fit_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QSpacerItem,
    QToolButton, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas

class Ui_CaloDetailsTestFitWidget(object):
    def setupUi(self, CaloDetailsTestFitWidget):
        if not CaloDetailsTestFitWidget.objectName():
            CaloDetailsTestFitWidget.setObjectName(u"CaloDetailsTestFitWidget")
        CaloDetailsTestFitWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(CaloDetailsTestFitWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonFit = QToolButton(CaloDetailsTestFitWidget)
        self.toolButtonFit.setObjectName(u"toolButtonFit")

        self.horizontalLayout.addWidget(self.toolButtonFit)

        self.toolButtonExport = QToolButton(CaloDetailsTestFitWidget)
        self.toolButtonExport.setObjectName(u"toolButtonExport")
        self.toolButtonExport.setPopupMode(QToolButton.MenuButtonPopup)

        self.horizontalLayout.addWidget(self.toolButtonExport)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(CaloDetailsTestFitWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(CaloDetailsTestFitWidget)

        QMetaObject.connectSlotsByName(CaloDetailsTestFitWidget)
    # setupUi

    def retranslateUi(self, CaloDetailsTestFitWidget):
        CaloDetailsTestFitWidget.setWindowTitle(QCoreApplication.translate("CaloDetailsTestFitWidget", u"Form", None))
        self.toolButtonFit.setText(QCoreApplication.translate("CaloDetailsTestFitWidget", u"Calculate Test Fit", None))
        self.toolButtonExport.setText(QCoreApplication.translate("CaloDetailsTestFitWidget", u"Export", None))
    # retranslateUi

