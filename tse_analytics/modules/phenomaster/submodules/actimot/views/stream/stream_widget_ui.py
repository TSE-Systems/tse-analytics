# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'stream_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QSpinBox, QToolButton, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas

class Ui_StreamWidget(object):
    def setupUi(self, StreamWidget):
        if not StreamWidget.objectName():
            StreamWidget.setObjectName(u"StreamWidget")
        self.verticalLayout = QVBoxLayout(StreamWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonCalculate = QToolButton(StreamWidget)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")
        self.toolButtonCalculate.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonCalculate)

        self.labelBins = QLabel(StreamWidget)
        self.labelBins.setObjectName(u"labelBins")

        self.horizontalLayout.addWidget(self.labelBins)

        self.spinBoxBins = QSpinBox(StreamWidget)
        self.spinBoxBins.setObjectName(u"spinBoxBins")
        self.spinBoxBins.setMinimum(1)
        self.spinBoxBins.setMaximum(32)
        self.spinBoxBins.setValue(10)

        self.horizontalLayout.addWidget(self.spinBoxBins)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(StreamWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(StreamWidget)

        QMetaObject.connectSlotsByName(StreamWidget)
    # setupUi

    def retranslateUi(self, StreamWidget):
        self.toolButtonCalculate.setText(QCoreApplication.translate("StreamWidget", u"Calculate", None))
        self.labelBins.setText(QCoreApplication.translate("StreamWidget", u"Bins:", None))
        pass
    # retranslateUi

