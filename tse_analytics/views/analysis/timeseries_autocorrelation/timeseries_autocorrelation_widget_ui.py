# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'timeseries_autocorrelation_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_TimeseriesAutocorrelationWidget(object):
    def setupUi(self, TimeseriesAutocorrelationWidget):
        if not TimeseriesAutocorrelationWidget.objectName():
            TimeseriesAutocorrelationWidget.setObjectName(u"TimeseriesAutocorrelationWidget")
        self.verticalLayout = QVBoxLayout(TimeseriesAutocorrelationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(TimeseriesAutocorrelationWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.canvas = MplCanvas(self.splitter)
        self.canvas.setObjectName(u"canvas")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.canvas)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_6 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBoxAnimal = QGroupBox(self.widgetSettings)
        self.groupBoxAnimal.setObjectName(u"groupBoxAnimal")
        self.horizontalLayout = QHBoxLayout(self.groupBoxAnimal)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.animalSelector = AnimalSelector(self.groupBoxAnimal)
        self.animalSelector.setObjectName(u"animalSelector")

        self.horizontalLayout.addWidget(self.animalSelector)


        self.verticalLayout_6.addWidget(self.groupBoxAnimal)

        self.groupBoxVariable = QGroupBox(self.widgetSettings)
        self.groupBoxVariable.setObjectName(u"groupBoxVariable")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxVariable)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.variableSelector = VariableSelector(self.groupBoxVariable)
        self.variableSelector.setObjectName(u"variableSelector")

        self.verticalLayout_4.addWidget(self.variableSelector)


        self.verticalLayout_6.addWidget(self.groupBoxVariable)

        self.pushButtonUpdate = QPushButton(self.widgetSettings)
        self.pushButtonUpdate.setObjectName(u"pushButtonUpdate")

        self.verticalLayout_6.addWidget(self.pushButtonUpdate)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")

        self.verticalLayout_6.addWidget(self.pushButtonAddReport)

        self.pushButtonHelp = QPushButton(self.widgetSettings)
        self.pushButtonHelp.setObjectName(u"pushButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButtonHelp.setIcon(icon)

        self.verticalLayout_6.addWidget(self.pushButtonHelp)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(TimeseriesAutocorrelationWidget)

        QMetaObject.connectSlotsByName(TimeseriesAutocorrelationWidget)
    # setupUi

    def retranslateUi(self, TimeseriesAutocorrelationWidget):
        self.groupBoxAnimal.setTitle(QCoreApplication.translate("TimeseriesAutocorrelationWidget", u"Animal", None))
        self.groupBoxVariable.setTitle(QCoreApplication.translate("TimeseriesAutocorrelationWidget", u"Variable", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("TimeseriesAutocorrelationWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("TimeseriesAutocorrelationWidget", u"Add to Report", None))
        self.pushButtonHelp.setText(QCoreApplication.translate("TimeseriesAutocorrelationWidget", u"Help", None))
        pass
    # retranslateUi

