# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'n_way_anova_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGroupBox,
    QHeaderView, QPushButton, QSizePolicy, QSplitter,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

from tse_analytics.views.misc.factors_table_widget import FactorsTableWidget
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget
import resources_rc

class Ui_NWayAnovaWidget(object):
    def setupUi(self, NWayAnovaWidget):
        if not NWayAnovaWidget.objectName():
            NWayAnovaWidget.setObjectName(u"NWayAnovaWidget")
        self.verticalLayout = QVBoxLayout(NWayAnovaWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(NWayAnovaWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.textEdit = QTextEdit(self.splitter)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy1)
        self.textEdit.setUndoRedoEnabled(False)
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setReadOnly(True)
        self.splitter.addWidget(self.textEdit)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_5 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
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
        self.tableWidgetFactors.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

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

        self.verticalLayout_5.addWidget(self.pushButtonUpdate)

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")

        self.verticalLayout_5.addWidget(self.pushButtonAddReport)

        self.pushButtonHelp = QPushButton(self.widgetSettings)
        self.pushButtonHelp.setObjectName(u"pushButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButtonHelp.setIcon(icon)

        self.verticalLayout_5.addWidget(self.pushButtonHelp)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(NWayAnovaWidget)

        QMetaObject.connectSlotsByName(NWayAnovaWidget)
    # setupUi

    def retranslateUi(self, NWayAnovaWidget):
        self.groupBoxFactors.setTitle(QCoreApplication.translate("NWayAnovaWidget", u"Factors", None))
        self.groupBoxDependentVariable.setTitle(QCoreApplication.translate("NWayAnovaWidget", u"Dependent Variable", None))
        self.groupBoxPAdjustment.setTitle(QCoreApplication.translate("NWayAnovaWidget", u"P-values adjustment", None))
        self.groupBoxEffectSizeType.setTitle(QCoreApplication.translate("NWayAnovaWidget", u"Effect size type", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("NWayAnovaWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("NWayAnovaWidget", u"Add to Report", None))
        self.pushButtonHelp.setText(QCoreApplication.translate("NWayAnovaWidget", u"Help", None))
        pass
    # retranslateUi

