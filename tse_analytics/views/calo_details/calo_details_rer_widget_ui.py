# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_details_rer_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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

class Ui_CaloDetailsRerWidget(object):
    def setupUi(self, CaloDetailsRerWidget):
        if not CaloDetailsRerWidget.objectName():
            CaloDetailsRerWidget.setObjectName(u"CaloDetailsRerWidget")
        CaloDetailsRerWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(CaloDetailsRerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBoxVariable = QComboBox(CaloDetailsRerWidget)
        self.comboBoxVariable.setObjectName(u"comboBoxVariable")

        self.horizontalLayout.addWidget(self.comboBoxVariable)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(CaloDetailsRerWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(CaloDetailsRerWidget)

        QMetaObject.connectSlotsByName(CaloDetailsRerWidget)
    # setupUi

    def retranslateUi(self, CaloDetailsRerWidget):
        CaloDetailsRerWidget.setWindowTitle(QCoreApplication.translate("CaloDetailsRerWidget", u"Form", None))
    # retranslateUi

