# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'datasets_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHeaderView, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_DatasetsWidget(object):
    def setupUi(self, DatasetsWidget):
        if not DatasetsWidget.objectName():
            DatasetsWidget.setObjectName(u"DatasetsWidget")
        self.verticalLayout = QVBoxLayout(DatasetsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.treeView = QTreeView(DatasetsWidget)
        self.treeView.setObjectName(u"treeView")
        self.treeView.header().setVisible(False)

        self.verticalLayout.addWidget(self.treeView)


        self.retranslateUi(DatasetsWidget)

        QMetaObject.connectSlotsByName(DatasetsWidget)
    # setupUi

    def retranslateUi(self, DatasetsWidget):
        pass
    # retranslateUi

