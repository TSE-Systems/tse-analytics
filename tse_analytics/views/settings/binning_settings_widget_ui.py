# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'binning_settings_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QLabel, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

from tse_analytics.views.settings.time_cycles_settings_widget import TimeCyclesSettingsWidget
from tse_analytics.views.settings.time_intervals_settings_widget import TimeIntervalsSettingsWidget
from tse_analytics.views.settings.time_phases_settings_widget import TimePhasesSettingsWidget

class Ui_BinningSettingsWidget(object):
    def setupUi(self, BinningSettingsWidget):
        if not BinningSettingsWidget.objectName():
            BinningSettingsWidget.setObjectName(u"BinningSettingsWidget")
        self.verticalLayout_2 = QVBoxLayout(BinningSettingsWidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(BinningSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 193, 124))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.widgetBinningOptions = QWidget(self.scrollAreaWidgetContents)
        self.widgetBinningOptions.setObjectName(u"widgetBinningOptions")
        self.formLayout = QFormLayout(self.widgetBinningOptions)
        self.formLayout.setObjectName(u"formLayout")
        self.applyBinningLabel = QLabel(self.widgetBinningOptions)
        self.applyBinningLabel.setObjectName(u"applyBinningLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.applyBinningLabel)

        self.applyBinningCheckBox = QCheckBox(self.widgetBinningOptions)
        self.applyBinningCheckBox.setObjectName(u"applyBinningCheckBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.applyBinningCheckBox)

        self.binningModeLabel = QLabel(self.widgetBinningOptions)
        self.binningModeLabel.setObjectName(u"binningModeLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.binningModeLabel)

        self.binningModeComboBox = QComboBox(self.widgetBinningOptions)
        self.binningModeComboBox.setObjectName(u"binningModeComboBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.binningModeComboBox)


        self.verticalLayout_3.addWidget(self.widgetBinningOptions)

        self.widgetTimeIntervalSettings = TimeIntervalsSettingsWidget(self.scrollAreaWidgetContents)
        self.widgetTimeIntervalSettings.setObjectName(u"widgetTimeIntervalSettings")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widgetTimeIntervalSettings.sizePolicy().hasHeightForWidth())
        self.widgetTimeIntervalSettings.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.widgetTimeIntervalSettings)

        self.widgetTimeCyclesSettings = TimeCyclesSettingsWidget(self.scrollAreaWidgetContents)
        self.widgetTimeCyclesSettings.setObjectName(u"widgetTimeCyclesSettings")
        sizePolicy.setHeightForWidth(self.widgetTimeCyclesSettings.sizePolicy().hasHeightForWidth())
        self.widgetTimeCyclesSettings.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.widgetTimeCyclesSettings)

        self.widgetTimePhasesSettings = TimePhasesSettingsWidget(self.scrollAreaWidgetContents)
        self.widgetTimePhasesSettings.setObjectName(u"widgetTimePhasesSettings")
        sizePolicy.setHeightForWidth(self.widgetTimePhasesSettings.sizePolicy().hasHeightForWidth())
        self.widgetTimePhasesSettings.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.widgetTimePhasesSettings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(BinningSettingsWidget)

        QMetaObject.connectSlotsByName(BinningSettingsWidget)
    # setupUi

    def retranslateUi(self, BinningSettingsWidget):
        self.applyBinningLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Apply Binning", None))
        self.binningModeLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Binning Mode", None))
        pass
    # retranslateUi

