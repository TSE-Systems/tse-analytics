# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'actimot_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QApplication, QFrame, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)
import resources_rc

class Ui_ActimotSettingsWidget(object):
    def setupUi(self, ActimotSettingsWidget):
        if not ActimotSettingsWidget.objectName():
            ActimotSettingsWidget.setObjectName(u"ActimotSettingsWidget")
        self.verticalLayout = QVBoxLayout(ActimotSettingsWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.scrollArea = QScrollArea(ActimotSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 284, 384))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.pushButtonResetSettings = QPushButton(self.scrollAreaWidgetContents)
        self.pushButtonResetSettings.setObjectName(u"pushButtonResetSettings")

        self.verticalLayout_2.addWidget(self.pushButtonResetSettings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(ActimotSettingsWidget)

        QMetaObject.connectSlotsByName(ActimotSettingsWidget)
    # setupUi

    def retranslateUi(self, ActimotSettingsWidget):
        self.pushButtonResetSettings.setText(QCoreApplication.translate("ActimotSettingsWidget", u"Reset Settings", None))
        pass
    # retranslateUi

