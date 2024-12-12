# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'time_cycles_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QSizePolicy, QTimeEdit, QVBoxLayout, QWidget)

class Ui_TimeCyclesSettingsWidget(object):
    def setupUi(self, TimeCyclesSettingsWidget):
        if not TimeCyclesSettingsWidget.objectName():
            TimeCyclesSettingsWidget.setObjectName(u"TimeCyclesSettingsWidget")
        TimeCyclesSettingsWidget.resize(330, 353)
        self.verticalLayout = QVBoxLayout(TimeCyclesSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxCycles = QGroupBox(TimeCyclesSettingsWidget)
        self.groupBoxCycles.setObjectName(u"groupBoxCycles")
        self.formLayout = QFormLayout(self.groupBoxCycles)
        self.formLayout.setObjectName(u"formLayout")
        self.labelLightCycleStart = QLabel(self.groupBoxCycles)
        self.labelLightCycleStart.setObjectName(u"labelLightCycleStart")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelLightCycleStart)

        self.timeEditLightCycleStart = QTimeEdit(self.groupBoxCycles)
        self.timeEditLightCycleStart.setObjectName(u"timeEditLightCycleStart")
        self.timeEditLightCycleStart.setTime(QTime(7, 0, 0))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.timeEditLightCycleStart)

        self.labelDarkCycleStart = QLabel(self.groupBoxCycles)
        self.labelDarkCycleStart.setObjectName(u"labelDarkCycleStart")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelDarkCycleStart)

        self.timeEditDarkCycleStart = QTimeEdit(self.groupBoxCycles)
        self.timeEditDarkCycleStart.setObjectName(u"timeEditDarkCycleStart")
        self.timeEditDarkCycleStart.setTime(QTime(19, 0, 0))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.timeEditDarkCycleStart)


        self.verticalLayout.addWidget(self.groupBoxCycles)


        self.retranslateUi(TimeCyclesSettingsWidget)

        QMetaObject.connectSlotsByName(TimeCyclesSettingsWidget)
    # setupUi

    def retranslateUi(self, TimeCyclesSettingsWidget):
        TimeCyclesSettingsWidget.setWindowTitle(QCoreApplication.translate("TimeCyclesSettingsWidget", u"Form", None))
        self.groupBoxCycles.setTitle(QCoreApplication.translate("TimeCyclesSettingsWidget", u"Light/Dark Cycles", None))
        self.labelLightCycleStart.setText(QCoreApplication.translate("TimeCyclesSettingsWidget", u"Light cycle start", None))
        self.labelDarkCycleStart.setText(QCoreApplication.translate("TimeCyclesSettingsWidget", u"Dark cycle start", None))
    # retranslateUi

