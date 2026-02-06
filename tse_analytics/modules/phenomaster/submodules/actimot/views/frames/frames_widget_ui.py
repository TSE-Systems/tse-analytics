# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frames_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSlider, QSpacerItem, QVBoxLayout, QWidget)

class Ui_FramesWidget(object):
    def setupUi(self, FramesWidget):
        if not FramesWidget.objectName():
            FramesWidget.setObjectName(u"FramesWidget")
        self.verticalLayout = QVBoxLayout(FramesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelFrameNumber = QLabel(FramesWidget)
        self.labelFrameNumber.setObjectName(u"labelFrameNumber")

        self.horizontalLayout.addWidget(self.labelFrameNumber)

        self.labelCentroid = QLabel(FramesWidget)
        self.labelCentroid.setObjectName(u"labelCentroid")

        self.horizontalLayout.addWidget(self.labelCentroid)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.labelFrameImage = QLabel(FramesWidget)
        self.labelFrameImage.setObjectName(u"labelFrameImage")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelFrameImage.sizePolicy().hasHeightForWidth())
        self.labelFrameImage.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.labelFrameImage)

        self.horizontalSlider = QSlider(FramesWidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMinimumSize(QSize(0, 30))
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.horizontalSlider.setTickInterval(10000)

        self.verticalLayout.addWidget(self.horizontalSlider)


        self.retranslateUi(FramesWidget)

        QMetaObject.connectSlotsByName(FramesWidget)
    # setupUi

    def retranslateUi(self, FramesWidget):
        self.labelFrameNumber.setText(QCoreApplication.translate("FramesWidget", u"Frame:", None))
        self.labelCentroid.setText(QCoreApplication.translate("FramesWidget", u"Centroid:", None))
        pass
    # retranslateUi

