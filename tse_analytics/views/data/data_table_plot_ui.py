# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)

from tse_analytics.views.data.plot_view import PlotView
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_DataPlotWidget(object):
    def setupUi(self, DataPlotWidget):
        if not DataPlotWidget.objectName():
            DataPlotWidget.setObjectName(u"DataPlotWidget")
        DataPlotWidget.resize(538, 607)
        self.verticalLayout = QVBoxLayout(DataPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(DataPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(DataPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.toolButtonDisplayErrors = QToolButton(DataPlotWidget)
        self.toolButtonDisplayErrors.setObjectName(u"toolButtonDisplayErrors")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-sorting-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonDisplayErrors.setIcon(icon)
        self.toolButtonDisplayErrors.setCheckable(True)
        self.toolButtonDisplayErrors.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.toolButtonDisplayErrors)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.plotView = PlotView(DataPlotWidget)
        self.plotView.setObjectName(u"plotView")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotView.sizePolicy().hasHeightForWidth())
        self.plotView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.plotView)


        self.retranslateUi(DataPlotWidget)

        QMetaObject.connectSlotsByName(DataPlotWidget)
    # setupUi

    def retranslateUi(self, DataPlotWidget):
        DataPlotWidget.setWindowTitle(QCoreApplication.translate("DataPlotWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("DataPlotWidget", u"Variable:", None))
        self.toolButtonDisplayErrors.setText(QCoreApplication.translate("DataPlotWidget", u"Display Errors", None))
    # retranslateUi
