# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trafficage_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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

class Ui_TraffiCageDialog(object):
    def setupUi(self, TraffiCageDialog):
        if not TraffiCageDialog.objectName():
            TraffiCageDialog.setObjectName(u"TraffiCageDialog")
        TraffiCageDialog.resize(922, 603)
        self.verticalLayout = QVBoxLayout(TraffiCageDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.toolButtonPreprocess = QToolButton(TraffiCageDialog)
        self.toolButtonPreprocess.setObjectName(u"toolButtonPreprocess")
        icon = QIcon()
        icon.addFile(u":/icons/preprocess.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonPreprocess.setIcon(icon)
        self.toolButtonPreprocess.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.toolbarLayout.addWidget(self.toolButtonPreprocess)

        self.toolButtonExport = QToolButton(TraffiCageDialog)
        self.toolButtonExport.setObjectName(u"toolButtonExport")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-export-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonExport.setIcon(icon1)
        self.toolButtonExport.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.toolbarLayout.addWidget(self.toolButtonExport)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(TraffiCageDialog)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonHelp.setIcon(icon2)

        self.toolbarLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.toolbarLayout)

        self.tabWidget = QTabWidget(TraffiCageDialog)
        self.tabWidget.setObjectName(u"tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(TraffiCageDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(TraffiCageDialog)
        self.buttonBox.accepted.connect(TraffiCageDialog.accept)
        self.buttonBox.rejected.connect(TraffiCageDialog.reject)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(TraffiCageDialog)
    # setupUi

    def retranslateUi(self, TraffiCageDialog):
        TraffiCageDialog.setWindowTitle(QCoreApplication.translate("TraffiCageDialog", u"TraffiCage", None))
        self.toolButtonPreprocess.setText(QCoreApplication.translate("TraffiCageDialog", u"Preprocess Data", None))
        self.toolButtonExport.setText(QCoreApplication.translate("TraffiCageDialog", u"Export data...", None))
    # retranslateUi

