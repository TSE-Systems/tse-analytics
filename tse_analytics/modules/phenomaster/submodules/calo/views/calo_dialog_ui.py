# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QSplitter, QTabWidget,
    QToolBox, QVBoxLayout, QWidget)
import resources_rc

class Ui_CaloDialog(object):
    def setupUi(self, CaloDialog):
        if not CaloDialog.objectName():
            CaloDialog.setObjectName(u"CaloDialog")
        CaloDialog.resize(1020, 705)
        CaloDialog.setProperty(u"sizeGripEnabled", True)
        self.verticalLayout = QVBoxLayout(CaloDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.splitter = QSplitter(CaloDialog)
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
        self.page.setGeometry(QRect(0, 0, 881, 665))
        self.toolBox.addItem(self.page, u"Page 1")
        self.splitter.addWidget(self.toolBox)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(CaloDialog)

        self.tabWidget.setCurrentIndex(-1)
        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(CaloDialog)
    # setupUi

    def retranslateUi(self, CaloDialog):
        CaloDialog.setWindowTitle(QCoreApplication.translate("CaloDialog", u"Calo", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("CaloDialog", u"Page 1", None))
    # retranslateUi

