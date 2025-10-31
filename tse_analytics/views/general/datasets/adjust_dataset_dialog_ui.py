# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'adjust_dataset_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDateTimeEdit,
    QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QTimeEdit,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_AdjustDatasetDialog(object):
    def setupUi(self, AdjustDatasetDialog):
        if not AdjustDatasetDialog.objectName():
            AdjustDatasetDialog.setObjectName(u"AdjustDatasetDialog")
        AdjustDatasetDialog.resize(924, 520)
        self.verticalLayout = QVBoxLayout(AdjustDatasetDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widgetMain = QWidget(AdjustDatasetDialog)
        self.widgetMain.setObjectName(u"widgetMain")
        self.horizontalLayout_4 = QHBoxLayout(self.widgetMain)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.widgetLeft = QWidget(self.widgetMain)
        self.widgetLeft.setObjectName(u"widgetLeft")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widgetLeft.sizePolicy().hasHeightForWidth())
        self.widgetLeft.setSizePolicy(sizePolicy)
        self.verticalLayout_4 = QVBoxLayout(self.widgetLeft)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.groupBoxRename = QGroupBox(self.widgetLeft)
        self.groupBoxRename.setObjectName(u"groupBoxRename")
        self.groupBoxRename.setCheckable(True)
        self.groupBoxRename.setChecked(False)
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxRename)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lineEditName = QLineEdit(self.groupBoxRename)
        self.lineEditName.setObjectName(u"lineEditName")

        self.verticalLayout_3.addWidget(self.lineEditName)


        self.verticalLayout_4.addWidget(self.groupBoxRename)

        self.groupBoxResampling = QGroupBox(self.widgetLeft)
        self.groupBoxResampling.setObjectName(u"groupBoxResampling")
        self.groupBoxResampling.setCheckable(True)
        self.groupBoxResampling.setChecked(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxResampling)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.timeEditResamplingInterval = QTimeEdit(self.groupBoxResampling)
        self.timeEditResamplingInterval.setObjectName(u"timeEditResamplingInterval")

        self.verticalLayout_2.addWidget(self.timeEditResamplingInterval)


        self.verticalLayout_4.addWidget(self.groupBoxResampling)

        self.groupBoxTrimTime = QGroupBox(self.widgetLeft)
        self.groupBoxTrimTime.setObjectName(u"groupBoxTrimTime")
        self.groupBoxTrimTime.setCheckable(True)
        self.groupBoxTrimTime.setChecked(False)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxTrimTime)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelTrimTimeStart = QLabel(self.groupBoxTrimTime)
        self.labelTrimTimeStart.setObjectName(u"labelTrimTimeStart")

        self.horizontalLayout_2.addWidget(self.labelTrimTimeStart)

        self.dateTimeEditTrimStart = QDateTimeEdit(self.groupBoxTrimTime)
        self.dateTimeEditTrimStart.setObjectName(u"dateTimeEditTrimStart")

        self.horizontalLayout_2.addWidget(self.dateTimeEditTrimStart)

        self.labelTrimTimeEnd = QLabel(self.groupBoxTrimTime)
        self.labelTrimTimeEnd.setObjectName(u"labelTrimTimeEnd")

        self.horizontalLayout_2.addWidget(self.labelTrimTimeEnd)

        self.dateTimeEditTrimEnd = QDateTimeEdit(self.groupBoxTrimTime)
        self.dateTimeEditTrimEnd.setObjectName(u"dateTimeEditTrimEnd")

        self.horizontalLayout_2.addWidget(self.dateTimeEditTrimEnd)


        self.verticalLayout_4.addWidget(self.groupBoxTrimTime)

        self.groupBoxExcludeTime = QGroupBox(self.widgetLeft)
        self.groupBoxExcludeTime.setObjectName(u"groupBoxExcludeTime")
        self.groupBoxExcludeTime.setCheckable(True)
        self.groupBoxExcludeTime.setChecked(False)
        self.horizontalLayout_3 = QHBoxLayout(self.groupBoxExcludeTime)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelExcludeTimeStart = QLabel(self.groupBoxExcludeTime)
        self.labelExcludeTimeStart.setObjectName(u"labelExcludeTimeStart")

        self.horizontalLayout_3.addWidget(self.labelExcludeTimeStart)

        self.dateTimeEditExcludeStart = QDateTimeEdit(self.groupBoxExcludeTime)
        self.dateTimeEditExcludeStart.setObjectName(u"dateTimeEditExcludeStart")

        self.horizontalLayout_3.addWidget(self.dateTimeEditExcludeStart)

        self.labelExcludeTimeEnd = QLabel(self.groupBoxExcludeTime)
        self.labelExcludeTimeEnd.setObjectName(u"labelExcludeTimeEnd")

        self.horizontalLayout_3.addWidget(self.labelExcludeTimeEnd)

        self.dateTimeEditExcludeEnd = QDateTimeEdit(self.groupBoxExcludeTime)
        self.dateTimeEditExcludeEnd.setObjectName(u"dateTimeEditExcludeEnd")

        self.horizontalLayout_3.addWidget(self.dateTimeEditExcludeEnd)


        self.verticalLayout_4.addWidget(self.groupBoxExcludeTime)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)


        self.horizontalLayout_4.addWidget(self.widgetLeft)

        self.groupBoxExcludeAnimals = QGroupBox(self.widgetMain)
        self.groupBoxExcludeAnimals.setObjectName(u"groupBoxExcludeAnimals")
        self.groupBoxExcludeAnimals.setCheckable(True)
        self.groupBoxExcludeAnimals.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxExcludeAnimals)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.tableWidgetAnimals = QTableWidget(self.groupBoxExcludeAnimals)
        self.tableWidgetAnimals.setObjectName(u"tableWidgetAnimals")
        self.tableWidgetAnimals.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tableWidgetAnimals.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidgetAnimals.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableWidgetAnimals.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableWidgetAnimals.setSortingEnabled(True)
        self.tableWidgetAnimals.verticalHeader().setVisible(False)
        self.tableWidgetAnimals.verticalHeader().setMinimumSectionSize(20)
        self.tableWidgetAnimals.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_5.addWidget(self.tableWidgetAnimals)


        self.horizontalLayout_4.addWidget(self.groupBoxExcludeAnimals)


        self.verticalLayout.addWidget(self.widgetMain)

        self.buttonBox = QDialogButtonBox(AdjustDatasetDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AdjustDatasetDialog)
        self.buttonBox.accepted.connect(AdjustDatasetDialog.accept)
        self.buttonBox.rejected.connect(AdjustDatasetDialog.reject)

        QMetaObject.connectSlotsByName(AdjustDatasetDialog)
    # setupUi

    def retranslateUi(self, AdjustDatasetDialog):
        AdjustDatasetDialog.setWindowTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Adjust Dataset", None))
        self.groupBoxRename.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Rename", None))
        self.groupBoxResampling.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Apply resampling", None))
        self.timeEditResamplingInterval.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"HH:mm:ss", None))
        self.groupBoxTrimTime.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Trim time", None))
        self.labelTrimTimeStart.setText(QCoreApplication.translate("AdjustDatasetDialog", u"Start:", None))
        self.dateTimeEditTrimStart.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"yyyy-MM-dd HH:mm:ss", None))
        self.labelTrimTimeEnd.setText(QCoreApplication.translate("AdjustDatasetDialog", u"End:", None))
        self.dateTimeEditTrimEnd.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"yyyy-MM-dd HH:mm:ss", None))
        self.groupBoxExcludeTime.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Exclude time", None))
        self.labelExcludeTimeStart.setText(QCoreApplication.translate("AdjustDatasetDialog", u"Start:", None))
        self.dateTimeEditExcludeStart.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"yyyy-MM-dd HH:mm:ss", None))
        self.labelExcludeTimeEnd.setText(QCoreApplication.translate("AdjustDatasetDialog", u"End:", None))
        self.dateTimeEditExcludeEnd.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"yyyy-MM-dd HH:mm:ss", None))
        self.groupBoxExcludeAnimals.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Exclude animals", None))
    # retranslateUi

