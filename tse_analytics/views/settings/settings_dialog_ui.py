# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QGroupBox, QLabel,
    QRadioButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(271, 281)
        self.verticalLayout = QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxHelpMode = QGroupBox(SettingsDialog)
        self.groupBoxHelpMode.setObjectName(u"groupBoxHelpMode")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxHelpMode)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.radioButtonOnline = QRadioButton(self.groupBoxHelpMode)
        self.radioButtonOnline.setObjectName(u"radioButtonOnline")
        self.radioButtonOnline.setChecked(True)

        self.verticalLayout_2.addWidget(self.radioButtonOnline)

        self.radioButtonOffline = QRadioButton(self.groupBoxHelpMode)
        self.radioButtonOffline.setObjectName(u"radioButtonOffline")

        self.verticalLayout_2.addWidget(self.radioButtonOffline)


        self.verticalLayout.addWidget(self.groupBoxHelpMode)

        self.groupBoxPlotsSettings = QGroupBox(SettingsDialog)
        self.groupBoxPlotsSettings.setObjectName(u"groupBoxPlotsSettings")
        self.formLayout = QFormLayout(self.groupBoxPlotsSettings)
        self.formLayout.setObjectName(u"formLayout")
        self.dpiLabel = QLabel(self.groupBoxPlotsSettings)
        self.dpiLabel.setObjectName(u"dpiLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.dpiLabel)

        self.dpiSpinBox = QSpinBox(self.groupBoxPlotsSettings)
        self.dpiSpinBox.setObjectName(u"dpiSpinBox")
        self.dpiSpinBox.setMaximum(1000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dpiSpinBox)

        self.figureWidthInchesLabel = QLabel(self.groupBoxPlotsSettings)
        self.figureWidthInchesLabel.setObjectName(u"figureWidthInchesLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.figureWidthInchesLabel)

        self.figureWidthInchesDoubleSpinBox = QDoubleSpinBox(self.groupBoxPlotsSettings)
        self.figureWidthInchesDoubleSpinBox.setObjectName(u"figureWidthInchesDoubleSpinBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.figureWidthInchesDoubleSpinBox)

        self.figureHeightInchesLabel = QLabel(self.groupBoxPlotsSettings)
        self.figureHeightInchesLabel.setObjectName(u"figureHeightInchesLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.figureHeightInchesLabel)

        self.figureHeightInchesDoubleSpinBox = QDoubleSpinBox(self.groupBoxPlotsSettings)
        self.figureHeightInchesDoubleSpinBox.setObjectName(u"figureHeightInchesDoubleSpinBox")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.figureHeightInchesDoubleSpinBox)


        self.verticalLayout.addWidget(self.groupBoxPlotsSettings)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
        self.groupBoxHelpMode.setTitle(QCoreApplication.translate("SettingsDialog", u"Help Mode", None))
        self.radioButtonOnline.setText(QCoreApplication.translate("SettingsDialog", u"Use online help", None))
        self.radioButtonOffline.setText(QCoreApplication.translate("SettingsDialog", u"Use offline help", None))
        self.groupBoxPlotsSettings.setTitle(QCoreApplication.translate("SettingsDialog", u"Plots Settings", None))
        self.dpiLabel.setText(QCoreApplication.translate("SettingsDialog", u"DPI", None))
        self.figureWidthInchesLabel.setText(QCoreApplication.translate("SettingsDialog", u"Figure Width (inches)", None))
        self.figureHeightInchesLabel.setText(QCoreApplication.translate("SettingsDialog", u"Figure Height (inches)", None))
    # retranslateUi

