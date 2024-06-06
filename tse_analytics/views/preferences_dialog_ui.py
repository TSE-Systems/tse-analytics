# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(446, 395)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxCsvImportSettings = QGroupBox(PreferencesDialog)
        self.groupBoxCsvImportSettings.setObjectName(u"groupBoxCsvImportSettings")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxCsvImportSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxDelimiter = QGroupBox(self.groupBoxCsvImportSettings)
        self.groupBoxDelimiter.setObjectName(u"groupBoxDelimiter")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxDelimiter)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.lineEditDelimiter = QLineEdit(self.groupBoxDelimiter)
        self.lineEditDelimiter.setObjectName(u"lineEditDelimiter")

        self.verticalLayout_4.addWidget(self.lineEditDelimiter)


        self.verticalLayout_3.addWidget(self.groupBoxDelimiter)

        self.groupBoxDecimalSeparator = QGroupBox(self.groupBoxCsvImportSettings)
        self.groupBoxDecimalSeparator.setObjectName(u"groupBoxDecimalSeparator")
        self._2 = QHBoxLayout(self.groupBoxDecimalSeparator)
        self._2.setObjectName(u"_2")
        self.radioButtonPoint = QRadioButton(self.groupBoxDecimalSeparator)
        self.radioButtonPoint.setObjectName(u"radioButtonPoint")
        self.radioButtonPoint.setChecked(True)

        self._2.addWidget(self.radioButtonPoint)

        self.radioButtonComma = QRadioButton(self.groupBoxDecimalSeparator)
        self.radioButtonComma.setObjectName(u"radioButtonComma")

        self._2.addWidget(self.radioButtonComma)


        self.verticalLayout_3.addWidget(self.groupBoxDecimalSeparator)

        self.groupBoxDateTimeSettings = QGroupBox(self.groupBoxCsvImportSettings)
        self.groupBoxDateTimeSettings.setObjectName(u"groupBoxDateTimeSettings")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxDateTimeSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBoxDayFirst = QCheckBox(self.groupBoxDateTimeSettings)
        self.checkBoxDayFirst.setObjectName(u"checkBoxDayFirst")

        self.verticalLayout_2.addWidget(self.checkBoxDayFirst)

        self.groupBoxDateTimeFormat = QGroupBox(self.groupBoxDateTimeSettings)
        self.groupBoxDateTimeFormat.setObjectName(u"groupBoxDateTimeFormat")
        self.groupBoxDateTimeFormat.setCheckable(True)
        self.groupBoxDateTimeFormat.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxDateTimeFormat)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.lineEditDateTimeFormat = QLineEdit(self.groupBoxDateTimeFormat)
        self.lineEditDateTimeFormat.setObjectName(u"lineEditDateTimeFormat")

        self.verticalLayout_5.addWidget(self.lineEditDateTimeFormat)

        self.labelExample = QLabel(self.groupBoxDateTimeFormat)
        self.labelExample.setObjectName(u"labelExample")

        self.verticalLayout_5.addWidget(self.labelExample)


        self.verticalLayout_2.addWidget(self.groupBoxDateTimeFormat)


        self.verticalLayout_3.addWidget(self.groupBoxDateTimeSettings)


        self.verticalLayout.addWidget(self.groupBoxCsvImportSettings)

        self.buttonBox = QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.groupBoxCsvImportSettings.setTitle(QCoreApplication.translate("PreferencesDialog", u"CSV Import Settings", None))
        self.groupBoxDelimiter.setTitle(QCoreApplication.translate("PreferencesDialog", u"Column Delimiter", None))
        self.groupBoxDecimalSeparator.setTitle(QCoreApplication.translate("PreferencesDialog", u"Decimal Separator", None))
        self.radioButtonPoint.setText(QCoreApplication.translate("PreferencesDialog", u"Point [.]", None))
        self.radioButtonComma.setText(QCoreApplication.translate("PreferencesDialog", u"Comma [,]", None))
        self.groupBoxDateTimeSettings.setTitle(QCoreApplication.translate("PreferencesDialog", u"DateTime Settings", None))
        self.checkBoxDayFirst.setText(QCoreApplication.translate("PreferencesDialog", u"Day first (DD/MM format dates, international and European format)", None))
        self.groupBoxDateTimeFormat.setTitle(QCoreApplication.translate("PreferencesDialog", u"Use exact DateTime format", None))
        self.labelExample.setText(QCoreApplication.translate("PreferencesDialog", u"Example: %Y-%m-%d %H:%M:%S.%f", None))
    # retranslateUi

