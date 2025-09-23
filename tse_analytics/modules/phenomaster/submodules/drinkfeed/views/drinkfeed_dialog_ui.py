# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'drinkfeed_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QSplitter, QTabWidget,
    QToolBox, QVBoxLayout, QWidget)
import resources_rc

class Ui_DrinkFeedDialog(object):
    def setupUi(self, DrinkFeedDialog):
        if not DrinkFeedDialog.objectName():
            DrinkFeedDialog.setObjectName(u"DrinkFeedDialog")
        DrinkFeedDialog.resize(1020, 854)
        self.verticalLayout = QVBoxLayout(DrinkFeedDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(DrinkFeedDialog)
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
        self.toolBox.setMaximumSize(QSize(300, 16777215))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 300, 806))
        self.toolBox.addItem(self.page, u"Page 1")
        self.splitter.addWidget(self.toolBox)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(DrinkFeedDialog)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(DrinkFeedDialog)
    # setupUi

    def retranslateUi(self, DrinkFeedDialog):
        DrinkFeedDialog.setWindowTitle(QCoreApplication.translate("DrinkFeedDialog", u"DrinkFeed", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("DrinkFeedDialog", u"Page 1", None))
    # retranslateUi

