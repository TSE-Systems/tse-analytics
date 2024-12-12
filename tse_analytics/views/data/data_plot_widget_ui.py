# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_plot_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QSplitter,
    QVBoxLayout, QWidget)

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
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
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

        self.groupBoxSplitMode = QGroupBox(self.widgetSettings)
        self.groupBoxSplitMode.setObjectName(u"groupBoxSplitMode")
        self.verticalLayout_7 = QVBoxLayout(self.groupBoxSplitMode)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.radioButtonSplitTotal = QRadioButton(self.groupBoxSplitMode)
        self.radioButtonSplitTotal.setObjectName(u"radioButtonSplitTotal")

        self.verticalLayout_7.addWidget(self.radioButtonSplitTotal)

        self.radioButtonSplitByAnimal = QRadioButton(self.groupBoxSplitMode)
        self.radioButtonSplitByAnimal.setObjectName(u"radioButtonSplitByAnimal")
        self.radioButtonSplitByAnimal.setChecked(True)

        self.verticalLayout_7.addWidget(self.radioButtonSplitByAnimal)

        self.radioButtonSplitByRun = QRadioButton(self.groupBoxSplitMode)
        self.radioButtonSplitByRun.setObjectName(u"radioButtonSplitByRun")

        self.verticalLayout_7.addWidget(self.radioButtonSplitByRun)

        self.radioButtonSplitByFactor = QRadioButton(self.groupBoxSplitMode)
        self.radioButtonSplitByFactor.setObjectName(u"radioButtonSplitByFactor")

        self.verticalLayout_7.addWidget(self.radioButtonSplitByFactor)

        self.factorSelector = FactorSelector(self.groupBoxSplitMode)
        self.factorSelector.setObjectName(u"factorSelector")
        self.factorSelector.setEnabled(False)

        self.verticalLayout_7.addWidget(self.factorSelector)


        self.verticalLayout.addWidget(self.groupBoxSplitMode)

        self.groupBoxDisplayErrors = QGroupBox(self.widgetSettings)
        self.groupBoxDisplayErrors.setObjectName(u"groupBoxDisplayErrors")
        self.groupBoxDisplayErrors.setCheckable(True)
        self.groupBoxDisplayErrors.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxDisplayErrors)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.radioButtonStandardError = QRadioButton(self.groupBoxDisplayErrors)
        self.radioButtonStandardError.setObjectName(u"radioButtonStandardError")
        self.radioButtonStandardError.setChecked(True)

        self.verticalLayout_5.addWidget(self.radioButtonStandardError)

        self.radioButtonStandardDeviation = QRadioButton(self.groupBoxDisplayErrors)
        self.radioButtonStandardDeviation.setObjectName(u"radioButtonStandardDeviation")

        self.verticalLayout_5.addWidget(self.radioButtonStandardDeviation)


        self.verticalLayout.addWidget(self.groupBoxDisplayErrors)

        self.checkBoxScatterPlot = QCheckBox(self.widgetSettings)
        self.checkBoxScatterPlot.setObjectName(u"checkBoxScatterPlot")

        self.verticalLayout.addWidget(self.checkBoxScatterPlot)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")

        self.verticalLayout.addWidget(self.pushButtonAddReport)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout_2.addWidget(self.splitter)


        self.retranslateUi(DataPlotWidget)

        QMetaObject.connectSlotsByName(DataPlotWidget)
    # setupUi

    def retranslateUi(self, DataPlotWidget):
        self.groupBoxVariable.setTitle(QCoreApplication.translate("DataPlotWidget", u"Variable", None))
        self.groupBoxSplitMode.setTitle(QCoreApplication.translate("DataPlotWidget", u"Split Mode", None))
        self.radioButtonSplitTotal.setText(QCoreApplication.translate("DataPlotWidget", u"Total", None))
        self.radioButtonSplitByAnimal.setText(QCoreApplication.translate("DataPlotWidget", u"By Animal", None))
        self.radioButtonSplitByRun.setText(QCoreApplication.translate("DataPlotWidget", u"By Run", None))
        self.radioButtonSplitByFactor.setText(QCoreApplication.translate("DataPlotWidget", u"By Factor", None))
        self.groupBoxDisplayErrors.setTitle(QCoreApplication.translate("DataPlotWidget", u"Display Errors", None))
        self.radioButtonStandardError.setText(QCoreApplication.translate("DataPlotWidget", u"Standard Error", None))
        self.radioButtonStandardDeviation.setText(QCoreApplication.translate("DataPlotWidget", u"Standard Deviation", None))
        self.checkBoxScatterPlot.setText(QCoreApplication.translate("DataPlotWidget", u"Scatter Plot", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("DataPlotWidget", u"Add to Report", None))
        pass
    # retranslateUi

