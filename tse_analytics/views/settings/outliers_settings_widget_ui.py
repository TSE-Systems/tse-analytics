# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'outliers_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGroupBox, QLabel, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_OutliersSettingsWidget(object):
    def setupUi(self, OutliersSettingsWidget):
        if not OutliersSettingsWidget.objectName():
            OutliersSettingsWidget.setObjectName(u"OutliersSettingsWidget")
        OutliersSettingsWidget.resize(546, 585)
        self.verticalLayout = QVBoxLayout(OutliersSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(OutliersSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 528, 567))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxIQR = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxIQR.setObjectName(u"groupBoxIQR")
        self.formLayout = QFormLayout(self.groupBoxIQR)
        self.formLayout.setObjectName(u"formLayout")
        self.labelDetect = QLabel(self.groupBoxIQR)
        self.labelDetect.setObjectName(u"labelDetect")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelDetect)

        self.checkBoxDetect = QCheckBox(self.groupBoxIQR)
        self.checkBoxDetect.setObjectName(u"checkBoxDetect")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.checkBoxDetect)

        self.labelCoefficient = QLabel(self.groupBoxIQR)
        self.labelCoefficient.setObjectName(u"labelCoefficient")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelCoefficient)

        self.doubleSpinBoxCoefficient = QDoubleSpinBox(self.groupBoxIQR)
        self.doubleSpinBoxCoefficient.setObjectName(u"doubleSpinBoxCoefficient")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBoxCoefficient)


        self.verticalLayout_3.addWidget(self.groupBoxIQR)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(OutliersSettingsWidget)

        QMetaObject.connectSlotsByName(OutliersSettingsWidget)
    # setupUi

    def retranslateUi(self, OutliersSettingsWidget):
        OutliersSettingsWidget.setWindowTitle(QCoreApplication.translate("OutliersSettingsWidget", u"Form", None))
        self.groupBoxIQR.setTitle(QCoreApplication.translate("OutliersSettingsWidget", u"Interquartile Range", None))
        self.labelDetect.setText(QCoreApplication.translate("OutliersSettingsWidget", u"Detect", None))
        self.labelCoefficient.setText(QCoreApplication.translate("OutliersSettingsWidget", u"Coefficient", None))
    # retranslateUi

