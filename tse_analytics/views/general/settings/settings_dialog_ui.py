# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
    QGroupBox, QRadioButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(149, 141)
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

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

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
    # retranslateUi

