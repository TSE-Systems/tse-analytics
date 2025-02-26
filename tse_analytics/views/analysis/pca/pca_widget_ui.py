# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pca_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHeaderView, QPushButton,
    QRadioButton, QSizePolicy, QSplitter, QTableWidgetItem,
    QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget
import resources_rc

class Ui_PcaWidget(object):
    def setupUi(self, PcaWidget):
        if not PcaWidget.objectName():
            PcaWidget.setObjectName(u"PcaWidget")
        self.verticalLayout = QVBoxLayout(PcaWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(PcaWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.canvas = MplCanvas(self.splitter)
        self.canvas.setObjectName(u"canvas")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)
        self.splitter.addWidget(self.canvas)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_2 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxVariables = QGroupBox(self.widgetSettings)
        self.groupBoxVariables.setObjectName(u"groupBoxVariables")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxVariables)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.tableWidgetVariables = VariablesTableWidget(self.groupBoxVariables)
        self.tableWidgetVariables.setObjectName(u"tableWidgetVariables")

        self.verticalLayout_4.addWidget(self.tableWidgetVariables)


        self.verticalLayout_2.addWidget(self.groupBoxVariables)

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

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")

        self.verticalLayout_2.addWidget(self.pushButtonAddReport)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(PcaWidget)

        QMetaObject.connectSlotsByName(PcaWidget)
    # setupUi

    def retranslateUi(self, PcaWidget):
        self.groupBoxVariables.setTitle(QCoreApplication.translate("PcaWidget", u"Variables", None))
        self.groupBoxSplitMode.setTitle(QCoreApplication.translate("PcaWidget", u"Split Mode", None))
        self.radioButtonSplitTotal.setText(QCoreApplication.translate("PcaWidget", u"Total", None))
        self.radioButtonSplitByAnimal.setText(QCoreApplication.translate("PcaWidget", u"By Animal", None))
        self.radioButtonSplitByRun.setText(QCoreApplication.translate("PcaWidget", u"By Run", None))
        self.radioButtonSplitByFactor.setText(QCoreApplication.translate("PcaWidget", u"By Factor", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("PcaWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("PcaWidget", u"Add to Report", None))
        pass
    # retranslateUi

