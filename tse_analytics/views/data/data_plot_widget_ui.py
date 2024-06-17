# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_plot_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QRadioButton,
    QSizePolicy, QSpacerItem, QSplitter, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_DataPlotWidget(object):
    def setupUi(self, DataPlotWidget):
        if not DataPlotWidget.objectName():
            DataPlotWidget.setObjectName(u"DataPlotWidget")
        self.verticalLayout_2 = QVBoxLayout(DataPlotWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(DataPlotWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.widgetPlot = QWidget(self.splitter)
        self.widgetPlot.setObjectName(u"widgetPlot")
        self.splitter.addWidget(self.widgetPlot)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.widgetSettings.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout = QVBoxLayout(self.widgetSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxVariable = QGroupBox(self.widgetSettings)
        self.groupBoxVariable.setObjectName(u"groupBoxVariable")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxVariable)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.variableSelector = VariableSelector(self.groupBoxVariable)
        self.variableSelector.setObjectName(u"variableSelector")

        self.verticalLayout_3.addWidget(self.variableSelector)


        self.verticalLayout.addWidget(self.groupBoxVariable)

        self.groupBoxFactor = QGroupBox(self.widgetSettings)
        self.groupBoxFactor.setObjectName(u"groupBoxFactor")
        self.groupBoxFactor.setCheckable(True)
        self.groupBoxFactor.setChecked(False)
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxFactor)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.factorSelector = FactorSelector(self.groupBoxFactor)
        self.factorSelector.setObjectName(u"factorSelector")

        self.verticalLayout_4.addWidget(self.factorSelector)


        self.verticalLayout.addWidget(self.groupBoxFactor)

        self.groupBoxDisplayErrors = QGroupBox(self.widgetSettings)
        self.groupBoxDisplayErrors.setObjectName(u"groupBoxDisplayErrors")
        self.groupBoxDisplayErrors.setCheckable(True)
        self.groupBoxDisplayErrors.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxDisplayErrors)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.radioButtonStandardDeviation = QRadioButton(self.groupBoxDisplayErrors)
        self.radioButtonStandardDeviation.setObjectName(u"radioButtonStandardDeviation")
        self.radioButtonStandardDeviation.setChecked(True)

        self.verticalLayout_5.addWidget(self.radioButtonStandardDeviation)

        self.radioButtonStandardError = QRadioButton(self.groupBoxDisplayErrors)
        self.radioButtonStandardError.setObjectName(u"radioButtonStandardError")

        self.verticalLayout_5.addWidget(self.radioButtonStandardError)


        self.verticalLayout.addWidget(self.groupBoxDisplayErrors)

        self.checkBoxScatterPlot = QCheckBox(self.widgetSettings)
        self.checkBoxScatterPlot.setObjectName(u"checkBoxScatterPlot")

        self.verticalLayout.addWidget(self.checkBoxScatterPlot)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout_2.addWidget(self.splitter)


        self.retranslateUi(DataPlotWidget)

        QMetaObject.connectSlotsByName(DataPlotWidget)
    # setupUi

    def retranslateUi(self, DataPlotWidget):
        self.groupBoxVariable.setTitle(QCoreApplication.translate("DataPlotWidget", u"Variable", None))
        self.groupBoxFactor.setTitle(QCoreApplication.translate("DataPlotWidget", u"Split by factor", None))
        self.groupBoxDisplayErrors.setTitle(QCoreApplication.translate("DataPlotWidget", u"Display Errors", None))
        self.radioButtonStandardDeviation.setText(QCoreApplication.translate("DataPlotWidget", u"Standard Deviation", None))
        self.radioButtonStandardError.setText(QCoreApplication.translate("DataPlotWidget", u"Standard Error", None))
        self.checkBoxScatterPlot.setText(QCoreApplication.translate("DataPlotWidget", u"Scatter Plot", None))
        pass
    # retranslateUi

