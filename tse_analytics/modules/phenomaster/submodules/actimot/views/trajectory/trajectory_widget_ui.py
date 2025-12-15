# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trajectory_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QSizePolicy,
    QSpacerItem, QSpinBox, QToolButton, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas

class Ui_TrajectoryWidget(object):
    def setupUi(self, TrajectoryWidget):
        if not TrajectoryWidget.objectName():
            TrajectoryWidget.setObjectName(u"TrajectoryWidget")
        self.verticalLayout = QVBoxLayout(TrajectoryWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonCalculate = QToolButton(TrajectoryWidget)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")
        self.toolButtonCalculate.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonCalculate)

        self.checkBoxDrawNPoints = QCheckBox(TrajectoryWidget)
        self.checkBoxDrawNPoints.setObjectName(u"checkBoxDrawNPoints")

        self.horizontalLayout.addWidget(self.checkBoxDrawNPoints)

        self.spinBoxN = QSpinBox(TrajectoryWidget)
        self.spinBoxN.setObjectName(u"spinBoxN")
        self.spinBoxN.setEnabled(False)
        self.spinBoxN.setMinimum(1)
        self.spinBoxN.setMaximum(1000000)
        self.spinBoxN.setValue(10000)

        self.horizontalLayout.addWidget(self.spinBoxN)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(TrajectoryWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(TrajectoryWidget)

        QMetaObject.connectSlotsByName(TrajectoryWidget)
    # setupUi

    def retranslateUi(self, TrajectoryWidget):
        self.toolButtonCalculate.setText(QCoreApplication.translate("TrajectoryWidget", u"Calculate", None))
        self.checkBoxDrawNPoints.setText(QCoreApplication.translate("TrajectoryWidget", u"Draw N points:", None))
        pass
    # retranslateUi

