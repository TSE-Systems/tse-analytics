# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'reports_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QVBoxLayout, QWidget)

from tse_analytics.views.misc.custom_text_edit import CustomTextEdit
import resources_rc

class Ui_ReportsWidget(object):
    def setupUi(self, ReportsWidget):
        if not ReportsWidget.objectName():
            ReportsWidget.setObjectName(u"ReportsWidget")
        ReportsWidget.resize(274, 210)
        self.verticalLayout = QVBoxLayout(ReportsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.editor = CustomTextEdit(ReportsWidget)
        self.editor.setObjectName(u"editor")

        self.verticalLayout.addWidget(self.editor)


        self.retranslateUi(ReportsWidget)

        QMetaObject.connectSlotsByName(ReportsWidget)
    # setupUi

    def retranslateUi(self, ReportsWidget):
        pass
    # retranslateUi

