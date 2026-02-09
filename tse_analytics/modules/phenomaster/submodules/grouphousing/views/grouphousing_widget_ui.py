# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'grouphousing_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_GroupHousingWidget(object):
    def setupUi(self, GroupHousingWidget):
        if not GroupHousingWidget.objectName():
            GroupHousingWidget.setObjectName(u"GroupHousingWidget")
        GroupHousingWidget.resize(1139, 869)
        self.verticalLayout = QVBoxLayout(GroupHousingWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.tabWidget = QTabWidget(GroupHousingWidget)
        self.tabWidget.setObjectName(u"tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(GroupHousingWidget)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(GroupHousingWidget)
    # setupUi

    def retranslateUi(self, GroupHousingWidget):
        GroupHousingWidget.setWindowTitle(QCoreApplication.translate("GroupHousingWidget", u"Group Housing", None))
    # retranslateUi

