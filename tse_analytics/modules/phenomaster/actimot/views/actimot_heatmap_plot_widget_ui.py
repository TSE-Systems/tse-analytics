# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'actimot_heatmap_plot_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QSpinBox, QToolButton,
    QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas

class Ui_ActimotHeatmapPlotWidget(object):
    def setupUi(self, ActimotHeatmapPlotWidget):
        if not ActimotHeatmapPlotWidget.objectName():
            ActimotHeatmapPlotWidget.setObjectName(u"ActimotHeatmapPlotWidget")
        ActimotHeatmapPlotWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(ActimotHeatmapPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonCalculate = QToolButton(ActimotHeatmapPlotWidget)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")

        self.horizontalLayout.addWidget(self.toolButtonCalculate)

        self.labelBins = QLabel(ActimotHeatmapPlotWidget)
        self.labelBins.setObjectName(u"labelBins")

        self.horizontalLayout.addWidget(self.labelBins)

        self.spinBoxBins = QSpinBox(ActimotHeatmapPlotWidget)
        self.spinBoxBins.setObjectName(u"spinBoxBins")
        self.spinBoxBins.setMinimum(1)
        self.spinBoxBins.setMaximum(1000)
        self.spinBoxBins.setValue(32)

        self.horizontalLayout.addWidget(self.spinBoxBins)

        self.checkBoxNormalize = QCheckBox(ActimotHeatmapPlotWidget)
        self.checkBoxNormalize.setObjectName(u"checkBoxNormalize")

        self.horizontalLayout.addWidget(self.checkBoxNormalize)

        self.checkBoxLog = QCheckBox(ActimotHeatmapPlotWidget)
        self.checkBoxLog.setObjectName(u"checkBoxLog")

        self.horizontalLayout.addWidget(self.checkBoxLog)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.canvas = MplCanvas(ActimotHeatmapPlotWidget)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.canvas)


        self.retranslateUi(ActimotHeatmapPlotWidget)

        QMetaObject.connectSlotsByName(ActimotHeatmapPlotWidget)
    # setupUi

    def retranslateUi(self, ActimotHeatmapPlotWidget):
        self.toolButtonCalculate.setText(QCoreApplication.translate("ActimotHeatmapPlotWidget", u"Calculate", None))
        self.labelBins.setText(QCoreApplication.translate("ActimotHeatmapPlotWidget", u"Bins:", None))
        self.checkBoxNormalize.setText(QCoreApplication.translate("ActimotHeatmapPlotWidget", u"Normalize", None))
        self.checkBoxLog.setText(QCoreApplication.translate("ActimotHeatmapPlotWidget", u"Log", None))
        pass
    # retranslateUi

