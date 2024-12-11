# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'actimot_frames_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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

class Ui_ActimotFramesWidget(object):
    def setupUi(self, ActimotFramesWidget):
        if not ActimotFramesWidget.objectName():
            ActimotFramesWidget.setObjectName(u"ActimotFramesWidget")
        self.verticalLayout = QVBoxLayout(ActimotFramesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelFrameNumber = QLabel(ActimotFramesWidget)
        self.labelFrameNumber.setObjectName(u"labelFrameNumber")

        self.horizontalLayout.addWidget(self.labelFrameNumber)

        self.labelCentroid = QLabel(ActimotFramesWidget)
        self.labelCentroid.setObjectName(u"labelCentroid")

        self.horizontalLayout.addWidget(self.labelCentroid)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.labelFrameImage = QLabel(ActimotFramesWidget)
        self.labelFrameImage.setObjectName(u"labelFrameImage")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelFrameImage.sizePolicy().hasHeightForWidth())
        self.labelFrameImage.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.labelFrameImage)

        self.horizontalSlider = QSlider(ActimotFramesWidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setMinimumSize(QSize(0, 30))
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.horizontalSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.horizontalSlider.setTickInterval(10000)

        self.verticalLayout.addWidget(self.horizontalSlider)


        self.retranslateUi(ActimotFramesWidget)

        QMetaObject.connectSlotsByName(ActimotFramesWidget)
    # setupUi

    def retranslateUi(self, ActimotFramesWidget):
        self.labelFrameNumber.setText(QCoreApplication.translate("ActimotFramesWidget", u"Frame:", None))
        self.labelCentroid.setText(QCoreApplication.translate("ActimotFramesWidget", u"Centroid:", None))
        pass
    # retranslateUi

