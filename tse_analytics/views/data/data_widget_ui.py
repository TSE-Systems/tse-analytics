# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QLabel,
    QSizePolicy, QSplitter, QToolButton, QVBoxLayout,
    QWidget)

from tse_analytics.views.data.data_plot_widget import DataPlotWidget
from tse_analytics.views.data.data_table_widget import DataTableWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_DataWidget(object):
    def setupUi(self, DataWidget):
        if not DataWidget.objectName():
            DataWidget.setObjectName(u"DataWidget")
        self.verticalLayout_2 = QVBoxLayout(DataWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitterHorizontal = QSplitter(DataWidget)
        self.splitterHorizontal.setObjectName(u"splitterHorizontal")
        self.splitterHorizontal.setOrientation(Qt.Horizontal)
        self.splitterVertical = QSplitter(self.splitterHorizontal)
        self.splitterVertical.setObjectName(u"splitterVertical")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitterVertical.sizePolicy().hasHeightForWidth())
        self.splitterVertical.setSizePolicy(sizePolicy)
        self.splitterVertical.setOrientation(Qt.Vertical)
        self.widgetTable = DataTableWidget(self.splitterVertical)
        self.widgetTable.setObjectName(u"widgetTable")
        self.splitterVertical.addWidget(self.widgetTable)
        self.widgetPlot = DataPlotWidget(self.splitterVertical)
        self.widgetPlot.setObjectName(u"widgetPlot")
        self.splitterVertical.addWidget(self.widgetPlot)
        self.splitterHorizontal.addWidget(self.splitterVertical)
        self.widgetSettings = QWidget(self.splitterHorizontal)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout = QVBoxLayout(self.widgetSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.comboBoxErrorType = QComboBox(self.widgetSettings)
        self.comboBoxErrorType.setObjectName(u"comboBoxErrorType")

        self.verticalLayout.addWidget(self.comboBoxErrorType)

        self.toolButtonDisplayErrors = QToolButton(self.widgetSettings)
        self.toolButtonDisplayErrors.setObjectName(u"toolButtonDisplayErrors")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-sorting-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonDisplayErrors.setIcon(icon)
        self.toolButtonDisplayErrors.setCheckable(True)
        self.toolButtonDisplayErrors.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.verticalLayout.addWidget(self.toolButtonDisplayErrors)

        self.variableSelector = VariableSelector(self.widgetSettings)
        self.variableSelector.setObjectName(u"variableSelector")

        self.verticalLayout.addWidget(self.variableSelector)

        self.label = QLabel(self.widgetSettings)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.checkBoxScatterPlot = QCheckBox(self.widgetSettings)
        self.checkBoxScatterPlot.setObjectName(u"checkBoxScatterPlot")

        self.verticalLayout.addWidget(self.checkBoxScatterPlot)

        self.splitterHorizontal.addWidget(self.widgetSettings)

        self.verticalLayout_2.addWidget(self.splitterHorizontal)


        self.retranslateUi(DataWidget)

        QMetaObject.connectSlotsByName(DataWidget)
    # setupUi

    def retranslateUi(self, DataWidget):
        self.toolButtonDisplayErrors.setText(QCoreApplication.translate("DataWidget", u"Display Errors", None))
        self.label.setText(QCoreApplication.translate("DataWidget", u"Variable:", None))
        self.checkBoxScatterPlot.setText(QCoreApplication.translate("DataWidget", u"Scatter Plot", None))
        pass
    # retranslateUi

