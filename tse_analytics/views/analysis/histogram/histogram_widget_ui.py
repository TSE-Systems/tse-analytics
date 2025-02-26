# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'histogram_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSplitter, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_HistogramWidget(object):
    def setupUi(self, HistogramWidget):
        if not HistogramWidget.objectName():
            HistogramWidget.setObjectName(u"HistogramWidget")
        self.verticalLayout = QVBoxLayout(HistogramWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(HistogramWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.canvas = MplCanvas(self.splitter)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)
        self.splitter.addWidget(self.canvas)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_2 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxVariable = QGroupBox(self.widgetSettings)
        self.groupBoxVariable.setObjectName(u"groupBoxVariable")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxVariable)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.variableSelector = VariableSelector(self.groupBoxVariable)
        self.variableSelector.setObjectName(u"variableSelector")

        self.verticalLayout_3.addWidget(self.variableSelector)


        self.verticalLayout_2.addWidget(self.groupBoxVariable)

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


        self.verticalLayout_2.addWidget(self.groupBoxSplitMode)

        self.pushButtonUpdate = QPushButton(self.widgetSettings)
        self.pushButtonUpdate.setObjectName(u"pushButtonUpdate")

        self.verticalLayout_2.addWidget(self.pushButtonUpdate)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")

        self.verticalLayout_2.addWidget(self.pushButtonAddReport)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(HistogramWidget)

        QMetaObject.connectSlotsByName(HistogramWidget)
    # setupUi

    def retranslateUi(self, HistogramWidget):
        self.groupBoxVariable.setTitle(QCoreApplication.translate("HistogramWidget", u"Variable", None))
        self.groupBoxSplitMode.setTitle(QCoreApplication.translate("HistogramWidget", u"Split Mode", None))
        self.radioButtonSplitTotal.setText(QCoreApplication.translate("HistogramWidget", u"Total", None))
        self.radioButtonSplitByAnimal.setText(QCoreApplication.translate("HistogramWidget", u"By Animal", None))
        self.radioButtonSplitByRun.setText(QCoreApplication.translate("HistogramWidget", u"By Run", None))
        self.radioButtonSplitByFactor.setText(QCoreApplication.translate("HistogramWidget", u"By Factor", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("HistogramWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("HistogramWidget", u"Add to Report", None))
        pass
    # retranslateUi

