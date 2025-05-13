# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_rer_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas

class Ui_CaloRerWidget(object):
    def setupUi(self, CaloRerWidget):
        if not CaloRerWidget.objectName():
            CaloRerWidget.setObjectName(u"CaloRerWidget")
        self.verticalLayout = QVBoxLayout(CaloRerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBoxVariable = QComboBox(CaloRerWidget)
        self.comboBoxVariable.setObjectName(u"comboBoxVariable")

        self.horizontalLayout.addWidget(self.comboBoxVariable)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(CaloRerWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(CaloRerWidget)

        QMetaObject.connectSlotsByName(CaloRerWidget)
    # setupUi

    def retranslateUi(self, CaloRerWidget):
        CaloRerWidget.setWindowTitle(QCoreApplication.translate("CaloRerWidget", u"Form", None))
    # retranslateUi

