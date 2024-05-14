# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'anova_widget.ui'
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGroupBox,
    QHBoxLayout, QHeaderView, QRadioButton, QSizePolicy,
    QSpacerItem, QSplitter, QTableWidget, QTableWidgetItem,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_AnovaWidget(object):
    def setupUi(self, AnovaWidget):
        if not AnovaWidget.objectName():
            AnovaWidget.setObjectName(u"AnovaWidget")
        AnovaWidget.resize(834, 774)
        self.verticalLayout = QVBoxLayout(AnovaWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(AnovaWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(AnovaWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(AnovaWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.webView = QWebEngineView(self.splitter)
        self.webView.setObjectName(u"webView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.webView)
        self.groupBoxSettings = QGroupBox(self.splitter)
        self.groupBoxSettings.setObjectName(u"groupBoxSettings")
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxSettings)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBoxMode = QGroupBox(self.groupBoxSettings)
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

        self.groupBoxPAdjustment = QGroupBox(self.groupBoxSettings)
        self.groupBoxPAdjustment.setObjectName(u"groupBoxPAdjustment")
        self.verticalLayout_7 = QVBoxLayout(self.groupBoxPAdjustment)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.comboBoxPAdjustment = QComboBox(self.groupBoxPAdjustment)
        self.comboBoxPAdjustment.setObjectName(u"comboBoxPAdjustment")

        self.verticalLayout_7.addWidget(self.comboBoxPAdjustment)


        self.verticalLayout_5.addWidget(self.groupBoxPAdjustment)

        self.groupBoxEffectSizeType = QGroupBox(self.groupBoxSettings)
        self.groupBoxEffectSizeType.setObjectName(u"groupBoxEffectSizeType")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxEffectSizeType)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.comboBoxEffectSizeType = QComboBox(self.groupBoxEffectSizeType)
        self.comboBoxEffectSizeType.setObjectName(u"comboBoxEffectSizeType")

        self.verticalLayout_6.addWidget(self.comboBoxEffectSizeType)


        self.verticalLayout_5.addWidget(self.groupBoxEffectSizeType)

        self.groupBoxDependentVariable = QGroupBox(self.groupBoxSettings)
        self.groupBoxDependentVariable.setObjectName(u"groupBoxDependentVariable")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxDependentVariable)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tableWidgetDependentVariable = QTableWidget(self.groupBoxDependentVariable)
        if (self.tableWidgetDependentVariable.columnCount() < 3):
            self.tableWidgetDependentVariable.setColumnCount(3)
        self.tableWidgetDependentVariable.setObjectName(u"tableWidgetDependentVariable")
        self.tableWidgetDependentVariable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidgetDependentVariable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidgetDependentVariable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetDependentVariable.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidgetDependentVariable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidgetDependentVariable.setSortingEnabled(True)
        self.tableWidgetDependentVariable.setColumnCount(3)
        self.tableWidgetDependentVariable.verticalHeader().setVisible(False)
        self.tableWidgetDependentVariable.verticalHeader().setMinimumSectionSize(20)
        self.tableWidgetDependentVariable.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_3.addWidget(self.tableWidgetDependentVariable)


        self.verticalLayout_5.addWidget(self.groupBoxDependentVariable)

        self.groupBoxCovariates = QGroupBox(self.groupBoxSettings)
        self.groupBoxCovariates.setObjectName(u"groupBoxCovariates")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxCovariates)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tableWidgetCovariates = QTableWidget(self.groupBoxCovariates)
        if (self.tableWidgetCovariates.columnCount() < 3):
            self.tableWidgetCovariates.setColumnCount(3)
        self.tableWidgetCovariates.setObjectName(u"tableWidgetCovariates")
        self.tableWidgetCovariates.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidgetCovariates.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tableWidgetCovariates.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetCovariates.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidgetCovariates.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidgetCovariates.setSortingEnabled(True)
        self.tableWidgetCovariates.setColumnCount(3)
        self.tableWidgetCovariates.verticalHeader().setVisible(False)
        self.tableWidgetCovariates.verticalHeader().setMinimumSectionSize(20)
        self.tableWidgetCovariates.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_4.addWidget(self.tableWidgetCovariates)


        self.verticalLayout_5.addWidget(self.groupBoxCovariates)

        self.splitter.addWidget(self.groupBoxSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(AnovaWidget)

        QMetaObject.connectSlotsByName(AnovaWidget)
    # setupUi

    def retranslateUi(self, AnovaWidget):
        AnovaWidget.setWindowTitle(QCoreApplication.translate("AnovaWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("AnovaWidget", u"Analyze", None))
        self.groupBoxSettings.setTitle(QCoreApplication.translate("AnovaWidget", u"Settings", None))
        self.groupBoxMode.setTitle(QCoreApplication.translate("AnovaWidget", u"Mode", None))
        self.radioButtonOneWayAnova.setText(QCoreApplication.translate("AnovaWidget", u"One-way ANOVA", None))
        self.radioButtonNWayAnova.setText(QCoreApplication.translate("AnovaWidget", u"N-way ANOVA", None))
        self.radioButtonRMAnova.setText(QCoreApplication.translate("AnovaWidget", u"Repeated measures ANOVA", None))
        self.radioButtonMixedAnova.setText(QCoreApplication.translate("AnovaWidget", u"Mixed-design ANOVA", None))
        self.radioButtonAncova.setText(QCoreApplication.translate("AnovaWidget", u"ANCOVA", None))
        self.groupBoxPAdjustment.setTitle(QCoreApplication.translate("AnovaWidget", u"P-values adjustment", None))
        self.groupBoxEffectSizeType.setTitle(QCoreApplication.translate("AnovaWidget", u"Effect size type", None))
        self.groupBoxDependentVariable.setTitle(QCoreApplication.translate("AnovaWidget", u"Dependent Variable", None))
        self.groupBoxCovariates.setTitle(QCoreApplication.translate("AnovaWidget", u"Covariates", None))
    # retranslateUi

