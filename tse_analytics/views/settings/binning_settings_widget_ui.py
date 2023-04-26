# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'binning_settings_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QLabel, QScrollArea, QSizePolicy,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_BinningSettingsWidget(object):
    def setupUi(self, BinningSettingsWidget):
        if not BinningSettingsWidget.objectName():
            BinningSettingsWidget.setObjectName(u"BinningSettingsWidget")
        BinningSettingsWidget.resize(546, 585)
        self.verticalLayout = QVBoxLayout(BinningSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(BinningSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 528, 567))
        self.formLayout = QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName(u"formLayout")
        self.groupingModeLabel = QLabel(self.scrollAreaWidgetContents)
        self.groupingModeLabel.setObjectName(u"groupingModeLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.groupingModeLabel)

        self.groupingModeComboBox = QComboBox(self.scrollAreaWidgetContents)
        self.groupingModeComboBox.setObjectName(u"groupingModeComboBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.groupingModeComboBox)

        self.applyBinningLabel = QLabel(self.scrollAreaWidgetContents)
        self.applyBinningLabel.setObjectName(u"applyBinningLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.applyBinningLabel)

        self.applyBinningCheckBox = QCheckBox(self.scrollAreaWidgetContents)
        self.applyBinningCheckBox.setObjectName(u"applyBinningCheckBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.applyBinningCheckBox)

        self.unitLabel = QLabel(self.scrollAreaWidgetContents)
        self.unitLabel.setObjectName(u"unitLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.unitLabel)

        self.unitComboBox = QComboBox(self.scrollAreaWidgetContents)
        self.unitComboBox.setObjectName(u"unitComboBox")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.unitComboBox)

        self.deltaLabel = QLabel(self.scrollAreaWidgetContents)
        self.deltaLabel.setObjectName(u"deltaLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.deltaLabel)

        self.deltaSpinBox = QSpinBox(self.scrollAreaWidgetContents)
        self.deltaSpinBox.setObjectName(u"deltaSpinBox")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.deltaSpinBox)

        self.operationLabel = QLabel(self.scrollAreaWidgetContents)
        self.operationLabel.setObjectName(u"operationLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.operationLabel)

        self.operationComboBox = QComboBox(self.scrollAreaWidgetContents)
        self.operationComboBox.setObjectName(u"operationComboBox")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.operationComboBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(BinningSettingsWidget)

        QMetaObject.connectSlotsByName(BinningSettingsWidget)
    # setupUi

    def retranslateUi(self, BinningSettingsWidget):
        BinningSettingsWidget.setWindowTitle(QCoreApplication.translate("BinningSettingsWidget", u"Form", None))
        self.groupingModeLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Grouping Mode", None))
        self.applyBinningLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Apply Binning", None))
        self.unitLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Unit", None))
        self.deltaLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Delta", None))
        self.operationLabel.setText(QCoreApplication.translate("BinningSettingsWidget", u"Operation", None))
    # retranslateUi

