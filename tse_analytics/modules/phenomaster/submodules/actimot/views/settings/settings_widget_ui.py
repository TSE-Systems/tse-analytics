# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)
import resources_rc

class Ui_SettingsWidget(object):
    def setupUi(self, SettingsWidget):
        if not SettingsWidget.objectName():
            SettingsWidget.setObjectName(u"SettingsWidget")
        self.verticalLayout = QVBoxLayout(SettingsWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.scrollArea = QScrollArea(SettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 244, 232))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.groupBoxSmoothing = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxSmoothing.setObjectName(u"groupBoxSmoothing")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxSmoothing.sizePolicy().hasHeightForWidth())
        self.groupBoxSmoothing.setSizePolicy(sizePolicy)
        self.groupBoxSmoothing.setCheckable(True)
        self.groupBoxSmoothing.setChecked(False)
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxSmoothing)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxWindowSize = QGroupBox(self.groupBoxSmoothing)
        self.groupBoxWindowSize.setObjectName(u"groupBoxWindowSize")
        self.groupBoxWindowSize.setCheckable(True)
        self.groupBoxWindowSize.setChecked(False)
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxWindowSize)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.spinBoxWindowSize = QSpinBox(self.groupBoxWindowSize)
        self.spinBoxWindowSize.setObjectName(u"spinBoxWindowSize")
        self.spinBoxWindowSize.setSingleStep(2)
        self.spinBoxWindowSize.setValue(11)

        self.verticalLayout_4.addWidget(self.spinBoxWindowSize)


        self.verticalLayout_3.addWidget(self.groupBoxWindowSize)

        self.widgetPolynomialOrder = QWidget(self.groupBoxSmoothing)
        self.widgetPolynomialOrder.setObjectName(u"widgetPolynomialOrder")
        self.horizontalLayout = QHBoxLayout(self.widgetPolynomialOrder)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelPolynomialOrder = QLabel(self.widgetPolynomialOrder)
        self.labelPolynomialOrder.setObjectName(u"labelPolynomialOrder")

        self.horizontalLayout.addWidget(self.labelPolynomialOrder)

        self.spinBoxPolynomialOrder = QSpinBox(self.widgetPolynomialOrder)
        self.spinBoxPolynomialOrder.setObjectName(u"spinBoxPolynomialOrder")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinBoxPolynomialOrder.sizePolicy().hasHeightForWidth())
        self.spinBoxPolynomialOrder.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.spinBoxPolynomialOrder)


        self.verticalLayout_3.addWidget(self.widgetPolynomialOrder)


        self.verticalLayout_2.addWidget(self.groupBoxSmoothing)

        self.pushButtonResetSettings = QPushButton(self.scrollAreaWidgetContents)
        self.pushButtonResetSettings.setObjectName(u"pushButtonResetSettings")

        self.verticalLayout_2.addWidget(self.pushButtonResetSettings)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(SettingsWidget)

        QMetaObject.connectSlotsByName(SettingsWidget)
    # setupUi

    def retranslateUi(self, SettingsWidget):
        self.groupBoxSmoothing.setTitle(QCoreApplication.translate("SettingsWidget", u"Smoothing (Savitzky-Golay filtering)", None))
        self.groupBoxWindowSize.setTitle(QCoreApplication.translate("SettingsWidget", u"Window Size", None))
        self.labelPolynomialOrder.setText(QCoreApplication.translate("SettingsWidget", u"Polynomial Order:", None))
        self.pushButtonResetSettings.setText(QCoreApplication.translate("SettingsWidget", u"Reset Settings", None))
        pass
    # retranslateUi

