# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'drinkfeed_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QSplitter, QTabWidget,
    QToolBox, QVBoxLayout, QWidget)
import resources_rc

class Ui_DrinkFeedWidget(object):
    def setupUi(self, DrinkFeedWidget):
        if not DrinkFeedWidget.objectName():
            DrinkFeedWidget.setObjectName(u"DrinkFeedWidget")
        DrinkFeedWidget.resize(1020, 854)
        self.verticalLayout = QVBoxLayout(DrinkFeedWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.splitter = QSplitter(DrinkFeedWidget)
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
        self.page.setGeometry(QRect(0, 0, 300, 814))
        self.toolBox.addItem(self.page, u"Page 1")
        self.splitter.addWidget(self.toolBox)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(DrinkFeedWidget)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(DrinkFeedWidget)
    # setupUi

    def retranslateUi(self, DrinkFeedWidget):
        DrinkFeedWidget.setWindowTitle(QCoreApplication.translate("DrinkFeedWidget", u"DrinkFeed", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("DrinkFeedWidget", u"Page 1", None))
    # retranslateUi

