# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'binning_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFormLayout, QFrame, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QScrollArea, QSizePolicy,
    QSpacerItem, QSpinBox, QTableView, QTimeEdit,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_BinningSettingsWidget(object):
    def setupUi(self, BinningSettingsWidget):
        if not BinningSettingsWidget.objectName():
            BinningSettingsWidget.setObjectName(u"BinningSettingsWidget")
        BinningSettingsWidget.resize(474, 597)
        self.verticalLayout_2 = QVBoxLayout(BinningSettingsWidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(BinningSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 474, 597))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widgetBinningOptions = QWidget(self.scrollAreaWidgetContents)
        self.widgetBinningOptions.setObjectName(u"widgetBinningOptions")
        self.formLayout = QFormLayout(self.widgetBinningOptions)
        self.formLayout.setObjectName(u"formLayout")
        self.applyBinningLabel = QLabel(self.widgetBinningOptions)
        self.applyBinningLabel.setObjectName(u"applyBinningLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.applyBinningLabel)

        self.applyBinningCheckBox = QCheckBox(self.widgetBinningOptions)
        self.applyBinningCheckBox.setObjectName(u"applyBinningCheckBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.applyBinningCheckBox)

        self.binningModeLabel = QLabel(self.widgetBinningOptions)
        self.binningModeLabel.setObjectName(u"binningModeLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.binningModeLabel)

        self.binningModeComboBox = QComboBox(self.widgetBinningOptions)
        self.binningModeComboBox.setObjectName(u"binningModeComboBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.binningModeComboBox)


        self.verticalLayout.addWidget(self.widgetBinningOptions)

        self.groupBoxIntervals = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxIntervals.setObjectName(u"groupBoxIntervals")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxIntervals.sizePolicy().hasHeightForWidth())
        self.groupBoxIntervals.setSizePolicy(sizePolicy)
        self.formLayout_2 = QFormLayout(self.groupBoxIntervals)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.unitLabel = QLabel(self.groupBoxIntervals)
        self.unitLabel.setObjectName(u"unitLabel")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.unitLabel)

        self.unitComboBox = QComboBox(self.groupBoxIntervals)
        self.unitComboBox.setObjectName(u"unitComboBox")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.unitComboBox)

        self.deltaLabel = QLabel(self.groupBoxIntervals)
        self.deltaLabel.setObjectName(u"deltaLabel")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.deltaLabel)

        self.deltaSpinBox = QSpinBox(self.groupBoxIntervals)
        self.deltaSpinBox.setObjectName(u"deltaSpinBox")
        self.deltaSpinBox.setMinimum(1)
        self.deltaSpinBox.setMaximum(1000)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.deltaSpinBox)


        self.verticalLayout.addWidget(self.groupBoxIntervals)

        self.groupBoxCycles = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxCycles.setObjectName(u"groupBoxCycles")
        sizePolicy.setHeightForWidth(self.groupBoxCycles.sizePolicy().hasHeightForWidth())
        self.groupBoxCycles.setSizePolicy(sizePolicy)
        self.formLayout_3 = QFormLayout(self.groupBoxCycles)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.labelLightCycleStart = QLabel(self.groupBoxCycles)
        self.labelLightCycleStart.setObjectName(u"labelLightCycleStart")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLightCycleStart)

        self.timeEditLightCycleStart = QTimeEdit(self.groupBoxCycles)
        self.timeEditLightCycleStart.setObjectName(u"timeEditLightCycleStart")
        self.timeEditLightCycleStart.setTime(QTime(7, 0, 0))

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.timeEditLightCycleStart)

        self.labelDarkCycleStart = QLabel(self.groupBoxCycles)
        self.labelDarkCycleStart.setObjectName(u"labelDarkCycleStart")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDarkCycleStart)

        self.timeEditDarkCycleStart = QTimeEdit(self.groupBoxCycles)
        self.timeEditDarkCycleStart.setObjectName(u"timeEditDarkCycleStart")
        self.timeEditDarkCycleStart.setTime(QTime(19, 0, 0))

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.timeEditDarkCycleStart)


        self.verticalLayout.addWidget(self.groupBoxCycles)

        self.groupBoxPhases = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxPhases.setObjectName(u"groupBoxPhases")
        sizePolicy.setHeightForWidth(self.groupBoxPhases.sizePolicy().hasHeightForWidth())
        self.groupBoxPhases.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxPhases)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tableViewTimePhases = QTableView(self.groupBoxPhases)
        self.tableViewTimePhases.setObjectName(u"tableViewTimePhases")
        self.tableViewTimePhases.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableViewTimePhases.verticalHeader().setMinimumSectionSize(20)
        self.tableViewTimePhases.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_3.addWidget(self.tableViewTimePhases)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAddPhase = QToolButton(self.groupBoxPhases)
        self.toolButtonAddPhase.setObjectName(u"toolButtonAddPhase")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-add-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonAddPhase.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonAddPhase)

        self.toolButtonDeletePhase = QToolButton(self.groupBoxPhases)
        self.toolButtonDeletePhase.setObjectName(u"toolButtonDeletePhase")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-minus-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonDeletePhase.setIcon(icon1)

        self.horizontalLayout.addWidget(self.toolButtonDeletePhase)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBoxPhases)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)


        self.retranslateUi(BinningSettingsWidget)

        QMetaObject.connectSlotsByName(BinningSettingsWidget)
    # setupUi

    def retranslateUi(self, BinningSettingsWidget):
        self.applyBinningLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Apply Binning", None))
        self.binningModeLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Binning Mode", None))
        self.groupBoxIntervals.setTitle(QCoreApplication.translate("BinningSettingsWidget", u"Time Intervals", None))
        self.unitLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Unit", None))
        self.deltaLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Delta", None))
        self.groupBoxCycles.setTitle(QCoreApplication.translate("BinningSettingsWidget", u"Light/Dark Cycles", None))
        self.labelLightCycleStart.setText(QCoreApplication.translate("BinningSettingsWidget", u"Light cycle start", None))
        self.labelDarkCycleStart.setText(QCoreApplication.translate("BinningSettingsWidget", u"Dark cycle start", None))
        self.groupBoxPhases.setTitle(QCoreApplication.translate("BinningSettingsWidget", u"Time Phases", None))
#if QT_CONFIG(tooltip)
        self.toolButtonAddPhase.setToolTip(QCoreApplication.translate("BinningSettingsWidget", u"Add time phase", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButtonDeletePhase.setToolTip(QCoreApplication.translate("BinningSettingsWidget", u"Delete selected time phase", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

