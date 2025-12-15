# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'grouphousing_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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

class Ui_GroupHousingDialog(object):
    def setupUi(self, GroupHousingDialog):
        if not GroupHousingDialog.objectName():
            GroupHousingDialog.setObjectName(u"GroupHousingDialog")
        GroupHousingDialog.resize(1139, 869)
        self.verticalLayout = QVBoxLayout(GroupHousingDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.tabWidget = QTabWidget(GroupHousingDialog)
        self.tabWidget.setObjectName(u"tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(GroupHousingDialog)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(GroupHousingDialog)
    # setupUi

    def retranslateUi(self, GroupHousingDialog):
        GroupHousingDialog.setWindowTitle(QCoreApplication.translate("GroupHousingDialog", u"Group Housing", None))
    # retranslateUi

