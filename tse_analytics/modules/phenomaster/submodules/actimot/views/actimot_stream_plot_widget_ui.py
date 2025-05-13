# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'actimot_stream_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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

class Ui_ActimotStreamPlotWidget(object):
    def setupUi(self, ActimotStreamPlotWidget):
        if not ActimotStreamPlotWidget.objectName():
            ActimotStreamPlotWidget.setObjectName(u"ActimotStreamPlotWidget")
        self.verticalLayout = QVBoxLayout(ActimotStreamPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonCalculate = QToolButton(ActimotStreamPlotWidget)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")
        self.toolButtonCalculate.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonCalculate)

        self.labelBins = QLabel(ActimotStreamPlotWidget)
        self.labelBins.setObjectName(u"labelBins")

        self.horizontalLayout.addWidget(self.labelBins)

        self.spinBoxBins = QSpinBox(ActimotStreamPlotWidget)
        self.spinBoxBins.setObjectName(u"spinBoxBins")
        self.spinBoxBins.setMinimum(1)
        self.spinBoxBins.setMaximum(1000)
        self.spinBoxBins.setValue(10)

        self.horizontalLayout.addWidget(self.spinBoxBins)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(ActimotStreamPlotWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(ActimotStreamPlotWidget)

        QMetaObject.connectSlotsByName(ActimotStreamPlotWidget)
    # setupUi

    def retranslateUi(self, ActimotStreamPlotWidget):
        self.toolButtonCalculate.setText(QCoreApplication.translate("ActimotStreamPlotWidget", u"Calculate", None))
        self.labelBins.setText(QCoreApplication.translate("ActimotStreamPlotWidget", u"Bins:", None))
        pass
    # retranslateUi

