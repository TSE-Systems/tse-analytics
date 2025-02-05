# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'intellicage_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
    QHBoxLayout, QSizePolicy, QSpacerItem, QTabWidget,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_IntelliCageDialog(object):
    def setupUi(self, IntelliCageDialog):
        if not IntelliCageDialog.objectName():
            IntelliCageDialog.setObjectName(u"IntelliCageDialog")
        IntelliCageDialog.resize(891, 568)
        self.verticalLayout = QVBoxLayout(IntelliCageDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.toolButtonPreprocess = QToolButton(IntelliCageDialog)
        self.toolButtonPreprocess.setObjectName(u"toolButtonPreprocess")
        icon = QIcon()
        icon.addFile(u":/icons/preprocess.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonPreprocess.setIcon(icon)
        self.toolButtonPreprocess.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.toolbarLayout.addWidget(self.toolButtonPreprocess)

        self.toolButtonExport = QToolButton(IntelliCageDialog)
        self.toolButtonExport.setObjectName(u"toolButtonExport")
        self.toolButtonExport.setEnabled(False)
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-export-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonExport.setIcon(icon1)
        self.toolButtonExport.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.toolbarLayout.addWidget(self.toolButtonExport)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(IntelliCageDialog)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonHelp.setIcon(icon2)

        self.toolbarLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.toolbarLayout)

        self.tabWidget = QTabWidget(IntelliCageDialog)
        self.tabWidget.setObjectName(u"tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(IntelliCageDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(IntelliCageDialog)
        self.buttonBox.accepted.connect(IntelliCageDialog.accept)
        self.buttonBox.rejected.connect(IntelliCageDialog.reject)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(IntelliCageDialog)
    # setupUi

    def retranslateUi(self, IntelliCageDialog):
        IntelliCageDialog.setWindowTitle(QCoreApplication.translate("IntelliCageDialog", u"IntelliCage", None))
        self.toolButtonPreprocess.setText(QCoreApplication.translate("IntelliCageDialog", u"Preprocess Data", None))
        self.toolButtonExport.setText(QCoreApplication.translate("IntelliCageDialog", u"Export data...", None))
    # retranslateUi

