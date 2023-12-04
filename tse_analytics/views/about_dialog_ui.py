# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
    QFormLayout, QGroupBox, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(337, 317)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelTitle = QLabel(AboutDialog)
        self.labelTitle.setObjectName(u"labelTitle")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.labelTitle.setFont(font)

        self.verticalLayout.addWidget(self.labelTitle)

        self.labelVersion = QLabel(AboutDialog)
        self.labelVersion.setObjectName(u"labelVersion")

        self.verticalLayout.addWidget(self.labelVersion)

        self.labelHardwareId = QLabel(AboutDialog)
        self.labelHardwareId.setObjectName(u"labelHardwareId")

        self.verticalLayout.addWidget(self.labelHardwareId)

        self.lineEditHardwareId = QLineEdit(AboutDialog)
        self.lineEditHardwareId.setObjectName(u"lineEditHardwareId")
        self.lineEditHardwareId.setReadOnly(True)

        self.verticalLayout.addWidget(self.lineEditHardwareId)

        self.groupBox = QGroupBox(AboutDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(self.groupBox)
        self.nameLineEdit.setObjectName(u"nameLineEdit")
        self.nameLineEdit.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.nameLineEdit)

        self.companyLabel = QLabel(self.groupBox)
        self.companyLabel.setObjectName(u"companyLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.companyLabel)

        self.companyLineEdit = QLineEdit(self.groupBox)
        self.companyLineEdit.setObjectName(u"companyLineEdit")
        self.companyLineEdit.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.companyLineEdit)

        self.emailLabel = QLabel(self.groupBox)
        self.emailLabel.setObjectName(u"emailLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.emailLabel)

        self.emailLineEdit = QLineEdit(self.groupBox)
        self.emailLineEdit.setObjectName(u"emailLineEdit")
        self.emailLineEdit.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.emailLineEdit)

        self.expirationLabel = QLabel(self.groupBox)
        self.expirationLabel.setObjectName(u"expirationLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.expirationLabel)

        self.expirationLineEdit = QLineEdit(self.groupBox)
        self.expirationLineEdit.setObjectName(u"expirationLineEdit")
        self.expirationLineEdit.setReadOnly(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.expirationLineEdit)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.accepted.connect(AboutDialog.accept)
        self.buttonBox.rejected.connect(AboutDialog.reject)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About", None))
        self.labelTitle.setText(QCoreApplication.translate("AboutDialog", u"TSE Analytics", None))
        self.labelVersion.setText(QCoreApplication.translate("AboutDialog", u"Version:", None))
        self.labelHardwareId.setText(QCoreApplication.translate("AboutDialog", u"Hardware ID:", None))
        self.groupBox.setTitle(QCoreApplication.translate("AboutDialog", u"License", None))
        self.nameLabel.setText(QCoreApplication.translate("AboutDialog", u"Name", None))
        self.companyLabel.setText(QCoreApplication.translate("AboutDialog", u"Company", None))
        self.emailLabel.setText(QCoreApplication.translate("AboutDialog", u"Email", None))
        self.expirationLabel.setText(QCoreApplication.translate("AboutDialog", u"Expiration", None))
    # retranslateUi

