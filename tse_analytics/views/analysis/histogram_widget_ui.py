# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'histogram_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
import resources_rc

class Ui_HistogramWidget(object):
    def setupUi(self, HistogramWidget):
        if not HistogramWidget.objectName():
            HistogramWidget.setObjectName(u"HistogramWidget")
        HistogramWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(HistogramWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(HistogramWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.labelBins = QLabel(HistogramWidget)
        self.labelBins.setObjectName(u"labelBins")

        self.horizontalLayout.addWidget(self.labelBins)

        self.spinBoxBins = QSpinBox(HistogramWidget)
        self.spinBoxBins.setObjectName(u"spinBoxBins")
        self.spinBoxBins.setMinimum(1)
        self.spinBoxBins.setMaximum(100)
        self.spinBoxBins.setValue(50)

        self.horizontalLayout.addWidget(self.spinBoxBins)

        self.toolButtonLogScale = QToolButton(HistogramWidget)
        self.toolButtonLogScale.setObjectName(u"toolButtonLogScale")
        self.toolButtonLogScale.setCheckable(True)

        self.horizontalLayout.addWidget(self.toolButtonLogScale)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(HistogramWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(HistogramWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(HistogramWidget)

        QMetaObject.connectSlotsByName(HistogramWidget)
    # setupUi

    def retranslateUi(self, HistogramWidget):
        HistogramWidget.setWindowTitle(QCoreApplication.translate("HistogramWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("HistogramWidget", u"Analyze", None))
        self.labelBins.setText(QCoreApplication.translate("HistogramWidget", u"Bins:", None))
        self.toolButtonLogScale.setText(QCoreApplication.translate("HistogramWidget", u"Log Scale", None))
    # retranslateUi

