# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
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

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

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
    # retranslateUi

