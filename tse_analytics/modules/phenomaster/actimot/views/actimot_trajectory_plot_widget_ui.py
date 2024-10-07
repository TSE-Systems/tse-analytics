# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'actimot_trajectory_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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

class Ui_ActimotTrajectoryPlotWidget(object):
    def setupUi(self, ActimotTrajectoryPlotWidget):
        if not ActimotTrajectoryPlotWidget.objectName():
            ActimotTrajectoryPlotWidget.setObjectName(u"ActimotTrajectoryPlotWidget")
        ActimotTrajectoryPlotWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(ActimotTrajectoryPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonCalculate = QToolButton(ActimotTrajectoryPlotWidget)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")

        self.horizontalLayout.addWidget(self.toolButtonCalculate)

        self.checkBoxDrawNPoints = QCheckBox(ActimotTrajectoryPlotWidget)
        self.checkBoxDrawNPoints.setObjectName(u"checkBoxDrawNPoints")

        self.horizontalLayout.addWidget(self.checkBoxDrawNPoints)

        self.spinBoxN = QSpinBox(ActimotTrajectoryPlotWidget)
        self.spinBoxN.setObjectName(u"spinBoxN")
        self.spinBoxN.setEnabled(False)
        self.spinBoxN.setMinimum(1)
        self.spinBoxN.setMaximum(1000000)
        self.spinBoxN.setValue(10000)

        self.horizontalLayout.addWidget(self.spinBoxN)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(ActimotTrajectoryPlotWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(ActimotTrajectoryPlotWidget)

        QMetaObject.connectSlotsByName(ActimotTrajectoryPlotWidget)
    # setupUi

    def retranslateUi(self, ActimotTrajectoryPlotWidget):
        self.toolButtonCalculate.setText(QCoreApplication.translate("ActimotTrajectoryPlotWidget", u"Calculate", None))
        self.checkBoxDrawNPoints.setText(QCoreApplication.translate("ActimotTrajectoryPlotWidget", u"Draw N points:", None))
        pass
    # retranslateUi

