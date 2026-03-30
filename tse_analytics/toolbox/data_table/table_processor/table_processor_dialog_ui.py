# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'table_processor_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QSpinBox, QTableView,
    QTableWidget, QTableWidgetItem, QTimeEdit, QToolButton,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_TableProcessorDialog(object):
    def setupUi(self, TableProcessorDialog):
        if not TableProcessorDialog.objectName():
            TableProcessorDialog.setObjectName(u"TableProcessorDialog")
        TableProcessorDialog.resize(765, 581)
        self.verticalLayout = QVBoxLayout(TableProcessorDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxVariable = QGroupBox(TableProcessorDialog)
        self.groupBoxVariable.setObjectName(u"groupBoxVariable")
        self.formLayout = QFormLayout(self.groupBoxVariable)
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(self.groupBoxVariable)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(self.groupBoxVariable)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.descriptionLabel = QLabel(self.groupBoxVariable)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.descriptionLineEdit = QLineEdit(self.groupBoxVariable)
        self.descriptionLineEdit.setObjectName(u"descriptionLineEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.descriptionLineEdit)


        self.verticalLayout.addWidget(self.groupBoxVariable)

        self.widgetLayoutH = QWidget(TableProcessorDialog)
        self.widgetLayoutH.setObjectName(u"widgetLayoutH")
        self.horizontalLayout = QHBoxLayout(self.widgetLayoutH)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBoxAnimals = QGroupBox(self.widgetLayoutH)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.groupBoxAnimals.setCheckable(True)
        self.groupBoxAnimals.setChecked(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableWidgetAnimals = QTableWidget(self.groupBoxAnimals)
        self.tableWidgetAnimals.setObjectName(u"tableWidgetAnimals")
        self.tableWidgetAnimals.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tableWidgetAnimals.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidgetAnimals.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableWidgetAnimals.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableWidgetAnimals.setSortingEnabled(True)
        self.tableWidgetAnimals.verticalHeader().setVisible(False)
        self.tableWidgetAnimals.verticalHeader().setMinimumSectionSize(20)
        self.tableWidgetAnimals.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_2.addWidget(self.tableWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)

        self.widgetLayoutV = QWidget(self.widgetLayoutH)
        self.widgetLayoutV.setObjectName(u"widgetLayoutV")
        self.widgetLayoutV.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.widgetLayoutV)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.groupBoxBinning = QGroupBox(self.widgetLayoutV)
        self.groupBoxBinning.setObjectName(u"groupBoxBinning")
        self.groupBoxBinning.setCheckable(True)
        self.groupBoxBinning.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxBinning)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.widgetBinning = QWidget(self.groupBoxBinning)
        self.widgetBinning.setObjectName(u"widgetBinning")
        self.formLayout_2 = QFormLayout(self.widgetBinning)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.binningModeLabel = QLabel(self.widgetBinning)
        self.binningModeLabel.setObjectName(u"binningModeLabel")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.binningModeLabel)

        self.binningModeComboBox = QComboBox(self.widgetBinning)
        self.binningModeComboBox.setObjectName(u"binningModeComboBox")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.binningModeComboBox)


        self.verticalLayout_5.addWidget(self.widgetBinning)

        self.widgetIntervals = QWidget(self.groupBoxBinning)
        self.widgetIntervals.setObjectName(u"widgetIntervals")
        self.horizontalLayout_3 = QHBoxLayout(self.widgetIntervals)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.deltaSpinBox = QSpinBox(self.widgetIntervals)
        self.deltaSpinBox.setObjectName(u"deltaSpinBox")
        self.deltaSpinBox.setMinimum(1)
        self.deltaSpinBox.setMaximum(1000)

        self.horizontalLayout_3.addWidget(self.deltaSpinBox)

        self.unitComboBox = QComboBox(self.widgetIntervals)
        self.unitComboBox.setObjectName(u"unitComboBox")

        self.horizontalLayout_3.addWidget(self.unitComboBox)


        self.verticalLayout_5.addWidget(self.widgetIntervals)

        self.widgetCycles = QWidget(self.groupBoxBinning)
        self.widgetCycles.setObjectName(u"widgetCycles")
        self.formLayout_4 = QFormLayout(self.widgetCycles)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setContentsMargins(0, 0, 0, 0)
        self.labelLightCycleStart = QLabel(self.widgetCycles)
        self.labelLightCycleStart.setObjectName(u"labelLightCycleStart")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLightCycleStart)

        self.timeEditLightCycleStart = QTimeEdit(self.widgetCycles)
        self.timeEditLightCycleStart.setObjectName(u"timeEditLightCycleStart")
        self.timeEditLightCycleStart.setTime(QTime(7, 0, 0))

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.timeEditLightCycleStart)

        self.labelDarkCycleStart = QLabel(self.widgetCycles)
        self.labelDarkCycleStart.setObjectName(u"labelDarkCycleStart")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDarkCycleStart)

        self.timeEditDarkCycleStart = QTimeEdit(self.widgetCycles)
        self.timeEditDarkCycleStart.setObjectName(u"timeEditDarkCycleStart")
        self.timeEditDarkCycleStart.setTime(QTime(19, 0, 0))

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.timeEditDarkCycleStart)


        self.verticalLayout_5.addWidget(self.widgetCycles)

        self.widgetPhases = QWidget(self.groupBoxBinning)
        self.widgetPhases.setObjectName(u"widgetPhases")
        self.verticalLayout_4 = QVBoxLayout(self.widgetPhases)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.tableViewTimePhases = QTableView(self.widgetPhases)
        self.tableViewTimePhases.setObjectName(u"tableViewTimePhases")
        self.tableViewTimePhases.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableViewTimePhases.verticalHeader().setMinimumSectionSize(20)
        self.tableViewTimePhases.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_4.addWidget(self.tableViewTimePhases)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.toolButtonAddPhase = QToolButton(self.widgetPhases)
        self.toolButtonAddPhase.setObjectName(u"toolButtonAddPhase")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-add-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonAddPhase.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.toolButtonAddPhase)

        self.toolButtonDeletePhase = QToolButton(self.widgetPhases)
        self.toolButtonDeletePhase.setObjectName(u"toolButtonDeletePhase")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-minus-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonDeletePhase.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.toolButtonDeletePhase)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)


        self.verticalLayout_5.addWidget(self.widgetPhases)


        self.verticalLayout_3.addWidget(self.groupBoxBinning)

        self.groupBoxGrouping = QGroupBox(self.widgetLayoutV)
        self.groupBoxGrouping.setObjectName(u"groupBoxGrouping")
        self.groupBoxGrouping.setCheckable(True)
        self.groupBoxGrouping.setChecked(False)
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxGrouping)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.comboBoxGrouping = QComboBox(self.groupBoxGrouping)
        self.comboBoxGrouping.setObjectName(u"comboBoxGrouping")

        self.verticalLayout_6.addWidget(self.comboBoxGrouping)


        self.verticalLayout_3.addWidget(self.groupBoxGrouping)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.widgetLayoutV)


        self.verticalLayout.addWidget(self.widgetLayoutH)

        self.buttonBox = QDialogButtonBox(TableProcessorDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(TableProcessorDialog)
        self.buttonBox.accepted.connect(TableProcessorDialog.accept)
        self.buttonBox.rejected.connect(TableProcessorDialog.reject)

        QMetaObject.connectSlotsByName(TableProcessorDialog)
    # setupUi

    def retranslateUi(self, TableProcessorDialog):
        TableProcessorDialog.setWindowTitle(QCoreApplication.translate("TableProcessorDialog", u"Add Derived Table", None))
        self.nameLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Name:", None))
        self.descriptionLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Description:", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Exclude Animals", None))
        self.groupBoxBinning.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Binning", None))
        self.binningModeLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Binning Mode", None))
        self.labelLightCycleStart.setText(QCoreApplication.translate("TableProcessorDialog", u"Light cycle start", None))
        self.labelDarkCycleStart.setText(QCoreApplication.translate("TableProcessorDialog", u"Dark cycle start", None))
#if QT_CONFIG(tooltip)
        self.toolButtonAddPhase.setToolTip(QCoreApplication.translate("TableProcessorDialog", u"Add time phase", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButtonDeletePhase.setToolTip(QCoreApplication.translate("TableProcessorDialog", u"Delete selected time phase", None))
#endif // QT_CONFIG(tooltip)
        self.groupBoxGrouping.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Group By", None))
    # retranslateUi

