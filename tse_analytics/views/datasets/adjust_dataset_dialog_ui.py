# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'adjust_dataset_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDateTimeEdit, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QRadioButton, QSizePolicy, QSpinBox, QTimeEdit,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_AdjustDatasetDialog(object):
    def setupUi(self, AdjustDatasetDialog):
        if not AdjustDatasetDialog.objectName():
            AdjustDatasetDialog.setObjectName(u"AdjustDatasetDialog")
        AdjustDatasetDialog.resize(362, 264)
        self.verticalLayout = QVBoxLayout(AdjustDatasetDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxResampling = QGroupBox(AdjustDatasetDialog)
        self.groupBoxResampling.setObjectName(u"groupBoxResampling")
        self.groupBoxResampling.setCheckable(True)
        self.groupBoxResampling.setChecked(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxResampling)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.timeEditResamplingInterval = QTimeEdit(self.groupBoxResampling)
        self.timeEditResamplingInterval.setObjectName(u"timeEditResamplingInterval")

        self.verticalLayout_2.addWidget(self.timeEditResamplingInterval)


        self.verticalLayout.addWidget(self.groupBoxResampling)

        self.groupBoxTimeShift = QGroupBox(AdjustDatasetDialog)
        self.groupBoxTimeShift.setObjectName(u"groupBoxTimeShift")
        self.groupBoxTimeShift.setCheckable(True)
        self.groupBoxTimeShift.setChecked(False)
        self.horizontalLayout = QHBoxLayout(self.groupBoxTimeShift)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelTimeShiftDays = QLabel(self.groupBoxTimeShift)
        self.labelTimeShiftDays.setObjectName(u"labelTimeShiftDays")

        self.horizontalLayout.addWidget(self.labelTimeShiftDays)

        self.spinBoxTimeShiftDays = QSpinBox(self.groupBoxTimeShift)
        self.spinBoxTimeShiftDays.setObjectName(u"spinBoxTimeShiftDays")
        self.spinBoxTimeShiftDays.setMinimumSize(QSize(50, 0))

        self.horizontalLayout.addWidget(self.spinBoxTimeShiftDays)

        self.labelTimeShiftTime = QLabel(self.groupBoxTimeShift)
        self.labelTimeShiftTime.setObjectName(u"labelTimeShiftTime")

        self.horizontalLayout.addWidget(self.labelTimeShiftTime)

        self.timeEditTimeShift = QTimeEdit(self.groupBoxTimeShift)
        self.timeEditTimeShift.setObjectName(u"timeEditTimeShift")

        self.horizontalLayout.addWidget(self.timeEditTimeShift)

        self.radioButtonTimeShiftMinus = QRadioButton(self.groupBoxTimeShift)
        self.radioButtonTimeShiftMinus.setObjectName(u"radioButtonTimeShiftMinus")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-minus-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.radioButtonTimeShiftMinus.setIcon(icon)
        self.radioButtonTimeShiftMinus.setChecked(True)

        self.horizontalLayout.addWidget(self.radioButtonTimeShiftMinus)

        self.radioButtonTimeShiftPlus = QRadioButton(self.groupBoxTimeShift)
        self.radioButtonTimeShiftPlus.setObjectName(u"radioButtonTimeShiftPlus")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-add-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.radioButtonTimeShiftPlus.setIcon(icon1)

        self.horizontalLayout.addWidget(self.radioButtonTimeShiftPlus)


        self.verticalLayout.addWidget(self.groupBoxTimeShift)

        self.groupBoxTrimTime = QGroupBox(AdjustDatasetDialog)
        self.groupBoxTrimTime.setObjectName(u"groupBoxTrimTime")
        self.groupBoxTrimTime.setCheckable(True)
        self.groupBoxTrimTime.setChecked(False)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxTrimTime)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelTrimTimeStart = QLabel(self.groupBoxTrimTime)
        self.labelTrimTimeStart.setObjectName(u"labelTrimTimeStart")

        self.horizontalLayout_2.addWidget(self.labelTrimTimeStart)

        self.dateTimeEditStart = QDateTimeEdit(self.groupBoxTrimTime)
        self.dateTimeEditStart.setObjectName(u"dateTimeEditStart")

        self.horizontalLayout_2.addWidget(self.dateTimeEditStart)

        self.labelTrimTimeEnd = QLabel(self.groupBoxTrimTime)
        self.labelTrimTimeEnd.setObjectName(u"labelTrimTimeEnd")

        self.horizontalLayout_2.addWidget(self.labelTrimTimeEnd)

        self.dateTimeEditEnd = QDateTimeEdit(self.groupBoxTrimTime)
        self.dateTimeEditEnd.setObjectName(u"dateTimeEditEnd")

        self.horizontalLayout_2.addWidget(self.dateTimeEditEnd)


        self.verticalLayout.addWidget(self.groupBoxTrimTime)

        self.buttonBox = QDialogButtonBox(AdjustDatasetDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AdjustDatasetDialog)
        self.buttonBox.accepted.connect(AdjustDatasetDialog.accept)
        self.buttonBox.rejected.connect(AdjustDatasetDialog.reject)

        QMetaObject.connectSlotsByName(AdjustDatasetDialog)
    # setupUi

    def retranslateUi(self, AdjustDatasetDialog):
        AdjustDatasetDialog.setWindowTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Adjust Dataset", None))
        self.groupBoxResampling.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Apply resampling", None))
        self.timeEditResamplingInterval.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"HH:mm:ss", None))
        self.groupBoxTimeShift.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Apply time shift", None))
        self.labelTimeShiftDays.setText(QCoreApplication.translate("AdjustDatasetDialog", u"Days", None))
        self.labelTimeShiftTime.setText(QCoreApplication.translate("AdjustDatasetDialog", u"HH:mm:ss", None))
        self.timeEditTimeShift.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"HH:mm:ss", None))
        self.groupBoxTrimTime.setTitle(QCoreApplication.translate("AdjustDatasetDialog", u"Trim time", None))
        self.labelTrimTimeStart.setText(QCoreApplication.translate("AdjustDatasetDialog", u"Start:", None))
        self.dateTimeEditStart.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"yyyy.MM.dd HH:mm:ss", None))
        self.labelTrimTimeEnd.setText(QCoreApplication.translate("AdjustDatasetDialog", u"End:", None))
        self.dateTimeEditEnd.setDisplayFormat(QCoreApplication.translate("AdjustDatasetDialog", u"yyyy.MM.dd HH:mm:ss", None))
    # retranslateUi

