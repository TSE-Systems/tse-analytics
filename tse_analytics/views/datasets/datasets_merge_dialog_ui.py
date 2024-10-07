# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'datasets_merge_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QHeaderView, QLineEdit, QRadioButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_DatasetsMergeDialog(object):
    def setupUi(self, DatasetsMergeDialog):
        if not DatasetsMergeDialog.objectName():
            DatasetsMergeDialog.setObjectName(u"DatasetsMergeDialog")
        DatasetsMergeDialog.resize(1157, 523)
        self.verticalLayout = QVBoxLayout(DatasetsMergeDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidget = QTableWidget(DatasetsMergeDialog)
        self.tableWidget.setObjectName(u"tableWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setMinimumSectionSize(20)
        self.tableWidget.verticalHeader().setDefaultSectionSize(20)

        self.horizontalLayout.addWidget(self.tableWidget)

        self.widgetSettings = QWidget(DatasetsMergeDialog)
        self.widgetSettings.setObjectName(u"widgetSettings")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widgetSettings.sizePolicy().hasHeightForWidth())
        self.widgetSettings.setSizePolicy(sizePolicy1)
        self.widgetSettings.setMinimumSize(QSize(300, 0))
        self.verticalLayout_2 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxName = QGroupBox(self.widgetSettings)
        self.groupBoxName.setObjectName(u"groupBoxName")
        self._3 = QVBoxLayout(self.groupBoxName)
        self._3.setObjectName(u"_3")
        self.lineEditName = QLineEdit(self.groupBoxName)
        self.lineEditName.setObjectName(u"lineEditName")

        self._3.addWidget(self.lineEditName)


        self.verticalLayout_2.addWidget(self.groupBoxName)

        self.groupBoxMergingMode = QGroupBox(self.widgetSettings)
        self.groupBoxMergingMode.setObjectName(u"groupBoxMergingMode")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxMergingMode)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButtonContinuousMode = QRadioButton(self.groupBoxMergingMode)
        self.radioButtonContinuousMode.setObjectName(u"radioButtonContinuousMode")
        self.radioButtonContinuousMode.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButtonContinuousMode)

        self.radioButtonOverlapMode = QRadioButton(self.groupBoxMergingMode)
        self.radioButtonOverlapMode.setObjectName(u"radioButtonOverlapMode")

        self.verticalLayout_3.addWidget(self.radioButtonOverlapMode)


        self.verticalLayout_2.addWidget(self.groupBoxMergingMode)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.checkBoxSingleRun = QCheckBox(self.widgetSettings)
        self.checkBoxSingleRun.setObjectName(u"checkBoxSingleRun")

        self.verticalLayout_2.addWidget(self.checkBoxSingleRun)


        self.horizontalLayout.addWidget(self.widgetSettings)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(DatasetsMergeDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DatasetsMergeDialog)
        self.buttonBox.accepted.connect(DatasetsMergeDialog.accept)
        self.buttonBox.rejected.connect(DatasetsMergeDialog.reject)

        QMetaObject.connectSlotsByName(DatasetsMergeDialog)
    # setupUi

    def retranslateUi(self, DatasetsMergeDialog):
        DatasetsMergeDialog.setWindowTitle(QCoreApplication.translate("DatasetsMergeDialog", u"Merge Datasets", None))
        self.groupBoxName.setTitle(QCoreApplication.translate("DatasetsMergeDialog", u"Merged dataset name", None))
        self.groupBoxMergingMode.setTitle(QCoreApplication.translate("DatasetsMergeDialog", u"Merging Mode", None))
        self.radioButtonContinuousMode.setText(QCoreApplication.translate("DatasetsMergeDialog", u"Continuous", None))
        self.radioButtonOverlapMode.setText(QCoreApplication.translate("DatasetsMergeDialog", u"Overlap", None))
#if QT_CONFIG(tooltip)
        self.checkBoxSingleRun.setToolTip(QCoreApplication.translate("DatasetsMergeDialog", u"Merged dataset will have a Run number for all records assigned to 1", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxSingleRun.setText(QCoreApplication.translate("DatasetsMergeDialog", u"Merge as a single run", None))
    # retranslateUi

