# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_details_dialog.ui'
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
    QHBoxLayout, QSizePolicy, QSpacerItem, QSplitter,
    QTabWidget, QToolBox, QToolButton, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_CaloDetailsDialog(object):
    def setupUi(self, CaloDetailsDialog):
        if not CaloDetailsDialog.objectName():
            CaloDetailsDialog.setObjectName(u"CaloDetailsDialog")
        CaloDetailsDialog.resize(1020, 854)
        self.verticalLayout = QVBoxLayout(CaloDetailsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.toolButtonCalculate = QToolButton(CaloDetailsDialog)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")

        self.toolbarLayout.addWidget(self.toolButtonCalculate)

        self.toolButtonResetSettings = QToolButton(CaloDetailsDialog)
        self.toolButtonResetSettings.setObjectName(u"toolButtonResetSettings")

        self.toolbarLayout.addWidget(self.toolButtonResetSettings)

        self.toolButtonExport = QToolButton(CaloDetailsDialog)
        self.toolButtonExport.setObjectName(u"toolButtonExport")

        self.toolbarLayout.addWidget(self.toolButtonExport)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(CaloDetailsDialog)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonHelp.setIcon(icon)

        self.toolbarLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.toolbarLayout)

        self.splitter = QSplitter(CaloDetailsDialog)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.splitter.addWidget(self.tabWidget)
        self.toolBox = QToolBox(self.splitter)
        self.toolBox.setObjectName(u"toolBox")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 873, 745))
        self.toolBox.addItem(self.page, u"Page 1")
        self.splitter.addWidget(self.toolBox)

        self.verticalLayout.addWidget(self.splitter)

        self.buttonBox = QDialogButtonBox(CaloDetailsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(CaloDetailsDialog)
        self.buttonBox.accepted.connect(CaloDetailsDialog.accept)
        self.buttonBox.rejected.connect(CaloDetailsDialog.reject)

        self.tabWidget.setCurrentIndex(-1)
        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(CaloDetailsDialog)
    # setupUi

    def retranslateUi(self, CaloDetailsDialog):
        CaloDetailsDialog.setWindowTitle(QCoreApplication.translate("CaloDetailsDialog", u"Calo Details", None))
        self.toolButtonCalculate.setText(QCoreApplication.translate("CaloDetailsDialog", u"Calculate prediction for selected boxes", None))
        self.toolButtonResetSettings.setText(QCoreApplication.translate("CaloDetailsDialog", u"Reset default settings", None))
        self.toolButtonExport.setText(QCoreApplication.translate("CaloDetailsDialog", u"Export selected data", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("CaloDetailsDialog", u"Page 1", None))
    # retranslateUi

