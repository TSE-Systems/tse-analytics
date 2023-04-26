# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'time_settings_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QListView,
    QScrollArea, QSizePolicy, QSpacerItem, QTimeEdit,
    QToolButton, QVBoxLayout, QWidget)

class Ui_TimeSettingsWidget(object):
    def setupUi(self, TimeSettingsWidget):
        if not TimeSettingsWidget.objectName():
            TimeSettingsWidget.setObjectName(u"TimeSettingsWidget")
        TimeSettingsWidget.resize(546, 585)
        self.verticalLayout = QVBoxLayout(TimeSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(TimeSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 528, 567))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxCycles = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxCycles.setObjectName(u"groupBoxCycles")
        self.formLayout = QFormLayout(self.groupBoxCycles)
        self.formLayout.setObjectName(u"formLayout")
        self.labelApply = QLabel(self.groupBoxCycles)
        self.labelApply.setObjectName(u"labelApply")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelApply)

        self.checkBoxApply = QCheckBox(self.groupBoxCycles)
        self.checkBoxApply.setObjectName(u"checkBoxApply")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.checkBoxApply)

        self.labelLightCycleStart = QLabel(self.groupBoxCycles)
        self.labelLightCycleStart.setObjectName(u"labelLightCycleStart")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.labelLightCycleStart)

        self.timeEditLightCycleStart = QTimeEdit(self.groupBoxCycles)
        self.timeEditLightCycleStart.setObjectName(u"timeEditLightCycleStart")
        self.timeEditLightCycleStart.setTime(QTime(7, 0, 0))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.timeEditLightCycleStart)

        self.labelDarkCycleStart = QLabel(self.groupBoxCycles)
        self.labelDarkCycleStart.setObjectName(u"labelDarkCycleStart")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.labelDarkCycleStart)

        self.timeEditDarkCycleStart = QTimeEdit(self.groupBoxCycles)
        self.timeEditDarkCycleStart.setObjectName(u"timeEditDarkCycleStart")
        self.timeEditDarkCycleStart.setTime(QTime(19, 0, 0))

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.timeEditDarkCycleStart)


        self.verticalLayout_3.addWidget(self.groupBoxCycles)

        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listView = QListView(self.groupBox_2)
        self.listView.setObjectName(u"listView")

        self.verticalLayout_2.addWidget(self.listView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButton_2 = QToolButton(self.groupBox_2)
        self.toolButton_2.setObjectName(u"toolButton_2")

        self.horizontalLayout.addWidget(self.toolButton_2)

        self.toolButton = QToolButton(self.groupBox_2)
        self.toolButton.setObjectName(u"toolButton")

        self.horizontalLayout.addWidget(self.toolButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(TimeSettingsWidget)

        QMetaObject.connectSlotsByName(TimeSettingsWidget)
    # setupUi

    def retranslateUi(self, TimeSettingsWidget):
        TimeSettingsWidget.setWindowTitle(QCoreApplication.translate("TimeSettingsWidget", u"Form", None))
        self.groupBoxCycles.setTitle(QCoreApplication.translate("TimeSettingsWidget", u"Light/Dark Cycles", None))
        self.labelApply.setText(QCoreApplication.translate("TimeSettingsWidget", u"Apply", None))
        self.labelLightCycleStart.setText(QCoreApplication.translate("TimeSettingsWidget", u"Light cycle start", None))
        self.labelDarkCycleStart.setText(QCoreApplication.translate("TimeSettingsWidget", u"Dark cycle start", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("TimeSettingsWidget", u"GroupBox", None))
        self.toolButton_2.setText(QCoreApplication.translate("TimeSettingsWidget", u"...", None))
        self.toolButton.setText(QCoreApplication.translate("TimeSettingsWidget", u"...", None))
    # retranslateUi

