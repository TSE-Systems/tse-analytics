# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_merged_csv_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
    QDialogButtonBox, QGroupBox, QHBoxLayout, QListWidget,
    QListWidgetItem, QRadioButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ExportMergedCsvDialog(object):
    def setupUi(self, ExportMergedCsvDialog):
        if not ExportMergedCsvDialog.objectName():
            ExportMergedCsvDialog.setObjectName(u"ExportMergedCsvDialog")
        ExportMergedCsvDialog.resize(493, 397)
        self.verticalLayout = QVBoxLayout(ExportMergedCsvDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxExtensions = QGroupBox(ExportMergedCsvDialog)
        self.groupBoxExtensions.setObjectName(u"groupBoxExtensions")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxExtensions)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidgetExtensions = QListWidget(self.groupBoxExtensions)
        self.listWidgetExtensions.setObjectName(u"listWidgetExtensions")

        self.verticalLayout_2.addWidget(self.listWidgetExtensions)


        self.horizontalLayout.addWidget(self.groupBoxExtensions)

        self.widgetSettings = QWidget(ExportMergedCsvDialog)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_3 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.groupBoxDelimiter = QGroupBox(self.widgetSettings)
        self.groupBoxDelimiter.setObjectName(u"groupBoxDelimiter")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxDelimiter)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.radioButtonDelimiterSemicolon = QRadioButton(self.groupBoxDelimiter)
        self.radioButtonDelimiterSemicolon.setObjectName(u"radioButtonDelimiterSemicolon")
        self.radioButtonDelimiterSemicolon.setChecked(True)

        self.verticalLayout_4.addWidget(self.radioButtonDelimiterSemicolon)

        self.radioButtonDelimiterComma = QRadioButton(self.groupBoxDelimiter)
        self.radioButtonDelimiterComma.setObjectName(u"radioButtonDelimiterComma")

        self.verticalLayout_4.addWidget(self.radioButtonDelimiterComma)

        self.radioButtonDelimiterTab = QRadioButton(self.groupBoxDelimiter)
        self.radioButtonDelimiterTab.setObjectName(u"radioButtonDelimiterTab")

        self.verticalLayout_4.addWidget(self.radioButtonDelimiterTab)


        self.verticalLayout_3.addWidget(self.groupBoxDelimiter)

        self.groupBoxFormat = QGroupBox(self.widgetSettings)
        self.groupBoxFormat.setObjectName(u"groupBoxFormat")
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxFormat)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.radioButtonFormatNew = QRadioButton(self.groupBoxFormat)
        self.radioButtonFormatNew.setObjectName(u"radioButtonFormatNew")
        self.radioButtonFormatNew.setChecked(True)

        self.verticalLayout_5.addWidget(self.radioButtonFormatNew)

        self.radioButtonFormatOld = QRadioButton(self.groupBoxFormat)
        self.radioButtonFormatOld.setObjectName(u"radioButtonFormatOld")

        self.verticalLayout_5.addWidget(self.radioButtonFormatOld)


        self.verticalLayout_3.addWidget(self.groupBoxFormat)

        self.checkBoxExportRegistrations = QCheckBox(self.widgetSettings)
        self.checkBoxExportRegistrations.setObjectName(u"checkBoxExportRegistrations")
        self.checkBoxExportRegistrations.setChecked(True)

        self.verticalLayout_3.addWidget(self.checkBoxExportRegistrations)

        self.checkBoxExportVariables = QCheckBox(self.widgetSettings)
        self.checkBoxExportVariables.setObjectName(u"checkBoxExportVariables")

        self.verticalLayout_3.addWidget(self.checkBoxExportVariables)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.widgetSettings)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(ExportMergedCsvDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ExportMergedCsvDialog)
        self.buttonBox.accepted.connect(ExportMergedCsvDialog.accept)
        self.buttonBox.rejected.connect(ExportMergedCsvDialog.reject)

        QMetaObject.connectSlotsByName(ExportMergedCsvDialog)
    # setupUi

    def retranslateUi(self, ExportMergedCsvDialog):
        ExportMergedCsvDialog.setWindowTitle(QCoreApplication.translate("ExportMergedCsvDialog", u"Export Merged CSV File", None))
        self.groupBoxExtensions.setTitle(QCoreApplication.translate("ExportMergedCsvDialog", u"Extensions", None))
        self.groupBoxDelimiter.setTitle(QCoreApplication.translate("ExportMergedCsvDialog", u"Delimiter", None))
        self.radioButtonDelimiterSemicolon.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"Semicolon [;]", None))
        self.radioButtonDelimiterComma.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"Comma [,]", None))
        self.radioButtonDelimiterTab.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"Tab", None))
        self.groupBoxFormat.setTitle(QCoreApplication.translate("ExportMergedCsvDialog", u"Format", None))
        self.radioButtonFormatNew.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"New Format", None))
        self.radioButtonFormatOld.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"Old Format", None))
        self.checkBoxExportRegistrations.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"Export Registrations", None))
        self.checkBoxExportVariables.setText(QCoreApplication.translate("ExportMergedCsvDialog", u"Export Variables", None))
    # retranslateUi

