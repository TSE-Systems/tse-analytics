# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_widget.ui'
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

class Ui_CaloWidget(object):
    def setupUi(self, CaloWidget):
        if not CaloWidget.objectName():
            CaloWidget.setObjectName(u"CaloWidget")
        CaloWidget.resize(1020, 705)
        CaloWidget.setProperty(u"sizeGripEnabled", True)
        self.verticalLayout = QVBoxLayout(CaloWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.splitter = QSplitter(CaloWidget)
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


        self.retranslateUi(CaloWidget)

        self.tabWidget.setCurrentIndex(-1)
        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(CaloWidget)
    # setupUi

    def retranslateUi(self, CaloWidget):
        CaloWidget.setWindowTitle(QCoreApplication.translate("CaloWidget", u"Calo", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("CaloWidget", u"Page 1", None))
    # retranslateUi

