# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'correlation_widget.ui'
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
    QSizePolicy, QSpacerItem, QSplitter, QTextEdit,
    QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_CorrelationWidget(object):
    def setupUi(self, CorrelationWidget):
        if not CorrelationWidget.objectName():
            CorrelationWidget.setObjectName(u"CorrelationWidget")
        self.verticalLayout = QVBoxLayout(CorrelationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitterHorizontal = QSplitter(CorrelationWidget)
        self.splitterHorizontal.setObjectName(u"splitterHorizontal")
        self.splitterHorizontal.setOrientation(Qt.Orientation.Horizontal)
        self.splitterVertical = QSplitter(self.splitterHorizontal)
        self.splitterVertical.setObjectName(u"splitterVertical")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitterVertical.sizePolicy().hasHeightForWidth())
        self.splitterVertical.setSizePolicy(sizePolicy)
        self.splitterVertical.setOrientation(Qt.Orientation.Vertical)
        self.canvas = MplCanvas(self.splitterVertical)
        self.canvas.setObjectName(u"canvas")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy1)
        self.splitterVertical.addWidget(self.canvas)
        self.textEdit = QTextEdit(self.splitterVertical)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setUndoRedoEnabled(False)
        self.textEdit.setReadOnly(True)
        self.splitterVertical.addWidget(self.textEdit)
        self.splitterHorizontal.addWidget(self.splitterVertical)
        self.widgetSettings = QWidget(self.splitterHorizontal)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_2 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxX = QGroupBox(self.widgetSettings)
        self.groupBoxX.setObjectName(u"groupBoxX")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxX)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.variableSelectorX = VariableSelector(self.groupBoxX)
        self.variableSelectorX.setObjectName(u"variableSelectorX")

        self.verticalLayout_4.addWidget(self.variableSelectorX)


        self.verticalLayout_2.addWidget(self.groupBoxX)

        self.groupBoxY = QGroupBox(self.widgetSettings)
        self.groupBoxY.setObjectName(u"groupBoxY")
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxY)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.variableSelectorY = VariableSelector(self.groupBoxY)
        self.variableSelectorY.setObjectName(u"variableSelectorY")

        self.verticalLayout_5.addWidget(self.variableSelectorY)


        self.verticalLayout_2.addWidget(self.groupBoxY)

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

        self.pushButtonHelp = QPushButton(self.widgetSettings)
        self.pushButtonHelp.setObjectName(u"pushButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButtonHelp.setIcon(icon)

        self.verticalLayout_2.addWidget(self.pushButtonHelp)

        self.splitterHorizontal.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitterHorizontal)


        self.retranslateUi(CorrelationWidget)

        QMetaObject.connectSlotsByName(CorrelationWidget)
    # setupUi

    def retranslateUi(self, CorrelationWidget):
        self.groupBoxX.setTitle(QCoreApplication.translate("CorrelationWidget", u"X", None))
        self.groupBoxY.setTitle(QCoreApplication.translate("CorrelationWidget", u"Y", None))
        self.groupBoxSplitMode.setTitle(QCoreApplication.translate("CorrelationWidget", u"Split Mode", None))
        self.radioButtonSplitTotal.setText(QCoreApplication.translate("CorrelationWidget", u"Total", None))
        self.radioButtonSplitByAnimal.setText(QCoreApplication.translate("CorrelationWidget", u"By Animal", None))
        self.radioButtonSplitByRun.setText(QCoreApplication.translate("CorrelationWidget", u"By Run", None))
        self.radioButtonSplitByFactor.setText(QCoreApplication.translate("CorrelationWidget", u"By Factor", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("CorrelationWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("CorrelationWidget", u"Add to Report", None))
        self.pushButtonHelp.setText(QCoreApplication.translate("CorrelationWidget", u"Help", None))
        pass
    # retranslateUi

