# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_table_widget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHeaderView,
    QPushButton, QRadioButton, QSizePolicy, QSplitter,
    QTableView, QTableWidgetItem, QTextEdit, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget
import resources_rc

class Ui_DataTableWidget(object):
    def setupUi(self, DataTableWidget):
        if not DataTableWidget.objectName():
            DataTableWidget.setObjectName(u"DataTableWidget")
        self.verticalLayout_4 = QVBoxLayout(DataTableWidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(DataTableWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.tableView = QTableView(self.splitter)
        self.tableView.setObjectName(u"tableView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.splitter.addWidget(self.tableView)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.widgetRightSide = QWidget(self.splitter)
        self.widgetRightSide.setObjectName(u"widgetRightSide")
        self.verticalLayout_2 = QVBoxLayout(self.widgetRightSide)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxVariables = QGroupBox(self.widgetRightSide)
        self.groupBoxVariables.setObjectName(u"groupBoxVariables")
        self.verticalLayout = QVBoxLayout(self.groupBoxVariables)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tableWidgetVariables = VariablesTableWidget(self.groupBoxVariables)
        self.tableWidgetVariables.setObjectName(u"tableWidgetVariables")

        self.verticalLayout.addWidget(self.tableWidgetVariables)


        self.verticalLayout_2.addWidget(self.groupBoxVariables)

        self.groupBoxSplitMode = QGroupBox(self.widgetRightSide)
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

        self.groupBoxDescriptive = QGroupBox(self.widgetRightSide)
        self.groupBoxDescriptive.setObjectName(u"groupBoxDescriptive")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxDescriptive)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.textEditDescriptiveStats = QTextEdit(self.groupBoxDescriptive)
        self.textEditDescriptiveStats.setObjectName(u"textEditDescriptiveStats")
        self.textEditDescriptiveStats.setUndoRedoEnabled(False)
        self.textEditDescriptiveStats.setLineWrapMode(QTextEdit.NoWrap)
        self.textEditDescriptiveStats.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.textEditDescriptiveStats)


        self.verticalLayout_2.addWidget(self.groupBoxDescriptive)

        self.pushButtonResizeColumns = QPushButton(self.widgetRightSide)
        self.pushButtonResizeColumns.setObjectName(u"pushButtonResizeColumns")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-resize-horizontal-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButtonResizeColumns.setIcon(icon)

        self.verticalLayout_2.addWidget(self.pushButtonResizeColumns)

        self.pushButtonAddReport = QPushButton(self.widgetRightSide)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")
        self.pushButtonAddReport.setEnabled(False)

        self.verticalLayout_2.addWidget(self.pushButtonAddReport)

        self.splitter.addWidget(self.widgetRightSide)

        self.verticalLayout_4.addWidget(self.splitter)


        self.retranslateUi(DataTableWidget)

        QMetaObject.connectSlotsByName(DataTableWidget)
    # setupUi

    def retranslateUi(self, DataTableWidget):
        self.groupBoxVariables.setTitle(QCoreApplication.translate("DataTableWidget", u"Variables", None))
        self.groupBoxSplitMode.setTitle(QCoreApplication.translate("DataTableWidget", u"Split Mode", None))
        self.radioButtonSplitTotal.setText(QCoreApplication.translate("DataTableWidget", u"Total", None))
        self.radioButtonSplitByAnimal.setText(QCoreApplication.translate("DataTableWidget", u"By Animal", None))
        self.radioButtonSplitByRun.setText(QCoreApplication.translate("DataTableWidget", u"By Run", None))
        self.radioButtonSplitByFactor.setText(QCoreApplication.translate("DataTableWidget", u"By Factor", None))
        self.groupBoxDescriptive.setTitle(QCoreApplication.translate("DataTableWidget", u"Descriptive Statistics", None))
        self.pushButtonResizeColumns.setText(QCoreApplication.translate("DataTableWidget", u"Resize Columns", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("DataTableWidget", u"Add to Report", None))
        pass
    # retranslateUi

