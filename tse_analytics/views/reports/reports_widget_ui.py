# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reports_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)
import resources_rc

class Ui_ReportsWidget(object):
    def setupUi(self, ReportsWidget):
        if not ReportsWidget.objectName():
            ReportsWidget.setObjectName(u"ReportsWidget")
        self.verticalLayout = QVBoxLayout(ReportsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButtonClear = QPushButton(ReportsWidget)
        self.pushButtonClear.setObjectName(u"pushButtonClear")

        self.horizontalLayout.addWidget(self.pushButtonClear)

        self.pushButtonExport = QPushButton(ReportsWidget)
        self.pushButtonExport.setObjectName(u"pushButtonExport")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-save-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonExport.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButtonExport)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.textEdit = QTextEdit(ReportsWidget)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout.addWidget(self.textEdit)


        self.retranslateUi(ReportsWidget)

        QMetaObject.connectSlotsByName(ReportsWidget)
    # setupUi

    def retranslateUi(self, ReportsWidget):
        self.pushButtonClear.setText(QCoreApplication.translate("ReportsWidget", u"Clear Report", None))
        self.pushButtonExport.setText(QCoreApplication.translate("ReportsWidget", u"Export Report...", None))
        pass
    # retranslateUi

