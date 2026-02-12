# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
    QLabel, QSizePolicy, QTabWidget, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(491, 335)
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

        self.tabWidget = QTabWidget(AboutDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabAbout = QWidget()
        self.tabAbout.setObjectName(u"tabAbout")
        self.verticalLayout_2 = QVBoxLayout(self.tabAbout)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.textBrowserAbout = QTextBrowser(self.tabAbout)
        self.textBrowserAbout.setObjectName(u"textBrowserAbout")
        self.textBrowserAbout.setOpenExternalLinks(True)

        self.verticalLayout_2.addWidget(self.textBrowserAbout)

        self.tabWidget.addTab(self.tabAbout, "")
        self.tabLicense = QWidget()
        self.tabLicense.setObjectName(u"tabLicense")
        self.verticalLayout_3 = QVBoxLayout(self.tabLicense)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.textBrowserLicense = QTextBrowser(self.tabLicense)
        self.textBrowserLicense.setObjectName(u"textBrowserLicense")
        self.textBrowserLicense.setOpenExternalLinks(True)

        self.verticalLayout_3.addWidget(self.textBrowserLicense)

        self.tabWidget.addTab(self.tabLicense, "")
        self.tabLibraries = QWidget()
        self.tabLibraries.setObjectName(u"tabLibraries")
        self.verticalLayout_4 = QVBoxLayout(self.tabLibraries)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.textBrowserLibraries = QTextBrowser(self.tabLibraries)
        self.textBrowserLibraries.setObjectName(u"textBrowserLibraries")
        self.textBrowserLibraries.setOpenExternalLinks(True)

        self.verticalLayout_4.addWidget(self.textBrowserLibraries)

        self.tabWidget.addTab(self.tabLibraries, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.accepted.connect(AboutDialog.accept)
        self.buttonBox.rejected.connect(AboutDialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About", None))
        self.labelTitle.setText(QCoreApplication.translate("AboutDialog", u"TSE Analytics", None))
        self.labelVersion.setText(QCoreApplication.translate("AboutDialog", u"Version Unknown", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAbout), QCoreApplication.translate("AboutDialog", u"About", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLicense), QCoreApplication.translate("AboutDialog", u"License agreement", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLibraries), QCoreApplication.translate("AboutDialog", u"Third-party libraries", None))
    # retranslateUi

