# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_table_widget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTableView, QVBoxLayout, QWidget)

from tse_analytics.views.misc.factor_selector import FactorSelector
import resources_rc

class Ui_DataTableWidget(object):
    def setupUi(self, DataTableWidget):
        if not DataTableWidget.objectName():
            DataTableWidget.setObjectName(u"DataTableWidget")
        self._2 = QVBoxLayout(DataTableWidget)
        self._2.setObjectName(u"_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelSplitMode = QLabel(DataTableWidget)
        self.labelSplitMode.setObjectName(u"labelSplitMode")

        self.horizontalLayout.addWidget(self.labelSplitMode)

        self.comboBoxSplitMode = QComboBox(DataTableWidget)
        self.comboBoxSplitMode.setObjectName(u"comboBoxSplitMode")

        self.horizontalLayout.addWidget(self.comboBoxSplitMode)

        self.labelFactor = QLabel(DataTableWidget)
        self.labelFactor.setObjectName(u"labelFactor")

        self.horizontalLayout.addWidget(self.labelFactor)

        self.factorSelector = FactorSelector(DataTableWidget)
        self.factorSelector.setObjectName(u"factorSelector")
        self.factorSelector.setEnabled(False)

        self.horizontalLayout.addWidget(self.factorSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.pushButtonResizeColumns = QPushButton(DataTableWidget)
        self.pushButtonResizeColumns.setObjectName(u"pushButtonResizeColumns")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-resize-horizontal-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonResizeColumns.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButtonResizeColumns)


        self._2.addLayout(self.horizontalLayout)

        self.tableView = QTableView(DataTableWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)

        self._2.addWidget(self.tableView)


        self.retranslateUi(DataTableWidget)

        QMetaObject.connectSlotsByName(DataTableWidget)
    # setupUi

    def retranslateUi(self, DataTableWidget):
        self.labelSplitMode.setText(QCoreApplication.translate("DataTableWidget", u"Split Mode:", None))
        self.labelFactor.setText(QCoreApplication.translate("DataTableWidget", u"Factor:", None))
        self.pushButtonResizeColumns.setText(QCoreApplication.translate("DataTableWidget", u"Resize Columns", None))
        pass
    # retranslateUi

