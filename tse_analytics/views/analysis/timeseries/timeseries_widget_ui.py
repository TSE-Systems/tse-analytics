# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'timeseries_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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

class Ui_TimeseriesWidget(object):
    def setupUi(self, TimeseriesWidget):
        if not TimeseriesWidget.objectName():
            TimeseriesWidget.setObjectName(u"TimeseriesWidget")
        TimeseriesWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(TimeseriesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(TimeseriesWidget)
        self.tabWidget.setObjectName(u"tabWidget")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(TimeseriesWidget)

        QMetaObject.connectSlotsByName(TimeseriesWidget)
    # setupUi

    def retranslateUi(self, TimeseriesWidget):
        TimeseriesWidget.setWindowTitle(QCoreApplication.translate("TimeseriesWidget", u"Form", None))
    # retranslateUi

