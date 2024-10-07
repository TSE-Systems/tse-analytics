# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'anova_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHeaderView,
    QPushButton, QRadioButton, QSizePolicy, QSplitter,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

from tse_analytics.views.misc.factors_table_widget import FactorsTableWidget
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget
import resources_rc

class Ui_AnovaWidget(object):
    def setupUi(self, AnovaWidget):
        if not AnovaWidget.objectName():
            AnovaWidget.setObjectName(u"AnovaWidget")
        self.verticalLayout = QVBoxLayout(AnovaWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(AnovaWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.textEdit = QTextEdit(self.splitter)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy1)
        self.textEdit.setUndoRedoEnabled(False)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.textEdit.setReadOnly(True)
        self.splitter.addWidget(self.textEdit)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_5 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBoxMode = QGroupBox(self.widgetSettings)
        self.groupBoxMode.setObjectName(u"groupBoxMode")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxMode)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.radioButtonOneWayAnova = QRadioButton(self.groupBoxMode)
        self.radioButtonOneWayAnova.setObjectName(u"radioButtonOneWayAnova")
        self.radioButtonOneWayAnova.setChecked(True)

        self.verticalLayout_2.addWidget(self.radioButtonOneWayAnova)

        self.radioButtonNWayAnova = QRadioButton(self.groupBoxMode)
        self.radioButtonNWayAnova.setObjectName(u"radioButtonNWayAnova")

        self.verticalLayout_2.addWidget(self.radioButtonNWayAnova)

        self.radioButtonRMAnova = QRadioButton(self.groupBoxMode)
        self.radioButtonRMAnova.setObjectName(u"radioButtonRMAnova")

        self.verticalLayout_2.addWidget(self.radioButtonRMAnova)

        self.radioButtonMixedAnova = QRadioButton(self.groupBoxMode)
        self.radioButtonMixedAnova.setObjectName(u"radioButtonMixedAnova")

        self.verticalLayout_2.addWidget(self.radioButtonMixedAnova)

        self.radioButtonAncova = QRadioButton(self.groupBoxMode)
        self.radioButtonAncova.setObjectName(u"radioButtonAncova")

        self.verticalLayout_2.addWidget(self.radioButtonAncova)


        self.verticalLayout_5.addWidget(self.groupBoxMode)

        self.groupBoxFactors = QGroupBox(self.widgetSettings)
        self.groupBoxFactors.setObjectName(u"groupBoxFactors")
        self.verticalLayout_8 = QVBoxLayout(self.groupBoxFactors)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.tableWidgetFactors = FactorsTableWidget(self.groupBoxFactors)
        self.tableWidgetFactors.setObjectName(u"tableWidgetFactors")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tableWidgetFactors.sizePolicy().hasHeightForWidth())
        self.tableWidgetFactors.setSizePolicy(sizePolicy2)
        self.tableWidgetFactors.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout_8.addWidget(self.tableWidgetFactors)


        self.verticalLayout_5.addWidget(self.groupBoxFactors)

        self.groupBoxDependentVariable = QGroupBox(self.widgetSettings)
        self.groupBoxDependentVariable.setObjectName(u"groupBoxDependentVariable")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxDependentVariable)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tableWidgetDependentVariable = VariablesTableWidget(self.groupBoxDependentVariable)
        self.tableWidgetDependentVariable.setObjectName(u"tableWidgetDependentVariable")

        self.verticalLayout_3.addWidget(self.tableWidgetDependentVariable)


        self.verticalLayout_5.addWidget(self.groupBoxDependentVariable)

        self.groupBoxCovariates = QGroupBox(self.widgetSettings)
        self.groupBoxCovariates.setObjectName(u"groupBoxCovariates")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxCovariates)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tableWidgetCovariates = VariablesTableWidget(self.groupBoxCovariates)
        self.tableWidgetCovariates.setObjectName(u"tableWidgetCovariates")

        self.verticalLayout_4.addWidget(self.tableWidgetCovariates)


        self.verticalLayout_5.addWidget(self.groupBoxCovariates)

        self.groupBoxPAdjustment = QGroupBox(self.widgetSettings)
        self.groupBoxPAdjustment.setObjectName(u"groupBoxPAdjustment")
        self.verticalLayout_7 = QVBoxLayout(self.groupBoxPAdjustment)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.comboBoxPAdjustment = QComboBox(self.groupBoxPAdjustment)
        self.comboBoxPAdjustment.setObjectName(u"comboBoxPAdjustment")

        self.verticalLayout_7.addWidget(self.comboBoxPAdjustment)


        self.verticalLayout_5.addWidget(self.groupBoxPAdjustment)

        self.groupBoxEffectSizeType = QGroupBox(self.widgetSettings)
        self.groupBoxEffectSizeType.setObjectName(u"groupBoxEffectSizeType")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxEffectSizeType)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.comboBoxEffectSizeType = QComboBox(self.groupBoxEffectSizeType)
        self.comboBoxEffectSizeType.setObjectName(u"comboBoxEffectSizeType")

        self.verticalLayout_6.addWidget(self.comboBoxEffectSizeType)


        self.verticalLayout_5.addWidget(self.groupBoxEffectSizeType)

        self.pushButtonUpdate = QPushButton(self.widgetSettings)
        self.pushButtonUpdate.setObjectName(u"pushButtonUpdate")
        self.pushButtonUpdate.setEnabled(False)

        self.verticalLayout_5.addWidget(self.pushButtonUpdate)

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")
        self.pushButtonAddReport.setEnabled(False)

        self.verticalLayout_5.addWidget(self.pushButtonAddReport)

        self.pushButtonHelp = QPushButton(self.widgetSettings)
        self.pushButtonHelp.setObjectName(u"pushButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButtonHelp.setIcon(icon)

        self.verticalLayout_5.addWidget(self.pushButtonHelp)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(AnovaWidget)

        QMetaObject.connectSlotsByName(AnovaWidget)
    # setupUi

    def retranslateUi(self, AnovaWidget):
        self.groupBoxMode.setTitle(QCoreApplication.translate("AnovaWidget", u"Mode", None))
        self.radioButtonOneWayAnova.setText(QCoreApplication.translate("AnovaWidget", u"One-way ANOVA", None))
        self.radioButtonNWayAnova.setText(QCoreApplication.translate("AnovaWidget", u"N-way ANOVA", None))
        self.radioButtonRMAnova.setText(QCoreApplication.translate("AnovaWidget", u"Repeated measures ANOVA", None))
        self.radioButtonMixedAnova.setText(QCoreApplication.translate("AnovaWidget", u"Mixed-design ANOVA", None))
        self.radioButtonAncova.setText(QCoreApplication.translate("AnovaWidget", u"ANCOVA", None))
        self.groupBoxFactors.setTitle(QCoreApplication.translate("AnovaWidget", u"Factors", None))
        self.groupBoxDependentVariable.setTitle(QCoreApplication.translate("AnovaWidget", u"Dependent Variable", None))
        self.groupBoxCovariates.setTitle(QCoreApplication.translate("AnovaWidget", u"Covariates", None))
        self.groupBoxPAdjustment.setTitle(QCoreApplication.translate("AnovaWidget", u"P-values adjustment", None))
        self.groupBoxEffectSizeType.setTitle(QCoreApplication.translate("AnovaWidget", u"Effect size type", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("AnovaWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("AnovaWidget", u"Add to Report", None))
        self.pushButtonHelp.setText(QCoreApplication.translate("AnovaWidget", u"Help", None))
        pass
    # retranslateUi

