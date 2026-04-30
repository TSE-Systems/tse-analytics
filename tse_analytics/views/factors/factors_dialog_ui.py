# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'factors_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
    QHBoxLayout, QHeaderView, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QStackedWidget, QTableView, QTimeEdit,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_FactorsDialog(object):
    def setupUi(self, FactorsDialog):
        if not FactorsDialog.objectName():
            FactorsDialog.setObjectName(u"FactorsDialog")
        FactorsDialog.resize(820, 513)
        self.verticalLayout_8 = QVBoxLayout(FactorsDialog)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxFactors = QGroupBox(FactorsDialog)
        self.groupBoxFactors.setObjectName(u"groupBoxFactors")
        self.verticalLayout = QVBoxLayout(self.groupBoxFactors)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidgetFactors = QListWidget(self.groupBoxFactors)
        self.listWidgetFactors.setObjectName(u"listWidgetFactors")

        self.verticalLayout.addWidget(self.listWidgetFactors)

        self.pushButtonAddFactor = QPushButton(self.groupBoxFactors)
        self.pushButtonAddFactor.setObjectName(u"pushButtonAddFactor")

        self.verticalLayout.addWidget(self.pushButtonAddFactor)

        self.pushButtonDeleteFactor = QPushButton(self.groupBoxFactors)
        self.pushButtonDeleteFactor.setObjectName(u"pushButtonDeleteFactor")
        self.pushButtonDeleteFactor.setEnabled(False)

        self.verticalLayout.addWidget(self.pushButtonDeleteFactor)


        self.horizontalLayout.addWidget(self.groupBoxFactors)

        self.groupBoxLevels = QGroupBox(FactorsDialog)
        self.groupBoxLevels.setObjectName(u"groupBoxLevels")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxLevels)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listWidgetLevels = QListWidget(self.groupBoxLevels)
        self.listWidgetLevels.setObjectName(u"listWidgetLevels")

        self.verticalLayout_3.addWidget(self.listWidgetLevels)

        self.pushButtonAddLevel = QPushButton(self.groupBoxLevels)
        self.pushButtonAddLevel.setObjectName(u"pushButtonAddLevel")
        self.pushButtonAddLevel.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonAddLevel)

        self.pushButtonDeleteLevel = QPushButton(self.groupBoxLevels)
        self.pushButtonDeleteLevel.setObjectName(u"pushButtonDeleteLevel")
        self.pushButtonDeleteLevel.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonDeleteLevel)

        self.pushButtonExtractLevels = QPushButton(self.groupBoxLevels)
        self.pushButtonExtractLevels.setObjectName(u"pushButtonExtractLevels")
        self.pushButtonExtractLevels.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonExtractLevels)

        self.comboBoxFields = QComboBox(self.groupBoxLevels)
        self.comboBoxFields.setObjectName(u"comboBoxFields")
        self.comboBoxFields.setEnabled(False)

        self.verticalLayout_3.addWidget(self.comboBoxFields)


        self.horizontalLayout.addWidget(self.groupBoxLevels)

        self.groupBoxConfig = QGroupBox(FactorsDialog)
        self.groupBoxConfig.setObjectName(u"groupBoxConfig")
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxConfig)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.stackedWidgetConfig = QStackedWidget(self.groupBoxConfig)
        self.stackedWidgetConfig.setObjectName(u"stackedWidgetConfig")
        self.pageAnimals = QWidget()
        self.pageAnimals.setObjectName(u"pageAnimals")
        self.verticalLayout_4 = QVBoxLayout(self.pageAnimals)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.labelAnimalsHint = QLabel(self.pageAnimals)
        self.labelAnimalsHint.setObjectName(u"labelAnimalsHint")

        self.verticalLayout_4.addWidget(self.labelAnimalsHint)

        self.listWidgetAnimals = QListWidget(self.pageAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")

        self.verticalLayout_4.addWidget(self.listWidgetAnimals)

        self.stackedWidgetConfig.addWidget(self.pageAnimals)
        self.pageCycles = QWidget()
        self.pageCycles.setObjectName(u"pageCycles")
        self.verticalLayout_6 = QVBoxLayout(self.pageCycles)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.labelCyclesHint = QLabel(self.pageCycles)
        self.labelCyclesHint.setObjectName(u"labelCyclesHint")

        self.verticalLayout_6.addWidget(self.labelCyclesHint)

        self.formLayoutCycles = QFormLayout()
        self.formLayoutCycles.setObjectName(u"formLayoutCycles")
        self.labelLightCycleStart = QLabel(self.pageCycles)
        self.labelLightCycleStart.setObjectName(u"labelLightCycleStart")

        self.formLayoutCycles.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLightCycleStart)

        self.timeEditLightStart = QTimeEdit(self.pageCycles)
        self.timeEditLightStart.setObjectName(u"timeEditLightStart")
        self.timeEditLightStart.setTime(QTime(7, 0, 0))

        self.formLayoutCycles.setWidget(0, QFormLayout.ItemRole.FieldRole, self.timeEditLightStart)

        self.labelDarkCycleStart = QLabel(self.pageCycles)
        self.labelDarkCycleStart.setObjectName(u"labelDarkCycleStart")

        self.formLayoutCycles.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDarkCycleStart)

        self.timeEditDarkStart = QTimeEdit(self.pageCycles)
        self.timeEditDarkStart.setObjectName(u"timeEditDarkStart")
        self.timeEditDarkStart.setTime(QTime(19, 0, 0))

        self.formLayoutCycles.setWidget(1, QFormLayout.ItemRole.FieldRole, self.timeEditDarkStart)


        self.verticalLayout_6.addLayout(self.formLayoutCycles)

        self.verticalSpacerCycles = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacerCycles)

        self.stackedWidgetConfig.addWidget(self.pageCycles)
        self.pagePhases = QWidget()
        self.pagePhases.setObjectName(u"pagePhases")
        self.verticalLayout_7 = QVBoxLayout(self.pagePhases)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.labelPhasesHint = QLabel(self.pagePhases)
        self.labelPhasesHint.setObjectName(u"labelPhasesHint")

        self.verticalLayout_7.addWidget(self.labelPhasesHint)

        self.tableViewPhases = QTableView(self.pagePhases)
        self.tableViewPhases.setObjectName(u"tableViewPhases")
        self.tableViewPhases.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableViewPhases.verticalHeader().setMinimumSectionSize(20)
        self.tableViewPhases.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_7.addWidget(self.tableViewPhases)

        self.horizontalLayoutPhases = QHBoxLayout()
        self.horizontalLayoutPhases.setObjectName(u"horizontalLayoutPhases")
        self.toolButtonAddPhase = QToolButton(self.pagePhases)
        self.toolButtonAddPhase.setObjectName(u"toolButtonAddPhase")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-add-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonAddPhase.setIcon(icon)

        self.horizontalLayoutPhases.addWidget(self.toolButtonAddPhase)

        self.toolButtonDeletePhase = QToolButton(self.pagePhases)
        self.toolButtonDeletePhase.setObjectName(u"toolButtonDeletePhase")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-minus-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonDeletePhase.setIcon(icon1)

        self.horizontalLayoutPhases.addWidget(self.toolButtonDeletePhase)

        self.horizontalSpacerPhases = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutPhases.addItem(self.horizontalSpacerPhases)


        self.verticalLayout_7.addLayout(self.horizontalLayoutPhases)

        self.stackedWidgetConfig.addWidget(self.pagePhases)
        self.pageAnimalProperty = QWidget()
        self.pageAnimalProperty.setObjectName(u"pageAnimalProperty")
        self.verticalLayoutAnimalProperty = QVBoxLayout(self.pageAnimalProperty)
        self.verticalLayoutAnimalProperty.setObjectName(u"verticalLayoutAnimalProperty")
        self.verticalLayoutAnimalProperty.setContentsMargins(0, 0, 0, 0)
        self.labelAnimalPropertyHint = QLabel(self.pageAnimalProperty)
        self.labelAnimalPropertyHint.setObjectName(u"labelAnimalPropertyHint")

        self.verticalLayoutAnimalProperty.addWidget(self.labelAnimalPropertyHint)

        self.comboBoxAnimalProperty = QComboBox(self.pageAnimalProperty)
        self.comboBoxAnimalProperty.setObjectName(u"comboBoxAnimalProperty")

        self.verticalLayoutAnimalProperty.addWidget(self.comboBoxAnimalProperty)

        self.verticalSpacerAnimalProperty = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutAnimalProperty.addItem(self.verticalSpacerAnimalProperty)

        self.stackedWidgetConfig.addWidget(self.pageAnimalProperty)
        self.pageColumn = QWidget()
        self.pageColumn.setObjectName(u"pageColumn")
        self.verticalLayoutColumn = QVBoxLayout(self.pageColumn)
        self.verticalLayoutColumn.setObjectName(u"verticalLayoutColumn")
        self.verticalLayoutColumn.setContentsMargins(0, 0, 0, 0)
        self.labelColumnHint = QLabel(self.pageColumn)
        self.labelColumnHint.setObjectName(u"labelColumnHint")

        self.verticalLayoutColumn.addWidget(self.labelColumnHint)

        self.comboBoxColumn = QComboBox(self.pageColumn)
        self.comboBoxColumn.setObjectName(u"comboBoxColumn")

        self.verticalLayoutColumn.addWidget(self.comboBoxColumn)

        self.verticalSpacerColumn = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutColumn.addItem(self.verticalSpacerColumn)

        self.stackedWidgetConfig.addWidget(self.pageColumn)
        self.pageTimeInterval = QWidget()
        self.pageTimeInterval.setObjectName(u"pageTimeInterval")
        self.verticalLayoutTimeInterval = QVBoxLayout(self.pageTimeInterval)
        self.verticalLayoutTimeInterval.setObjectName(u"verticalLayoutTimeInterval")
        self.verticalLayoutTimeInterval.setContentsMargins(0, 0, 0, 0)
        self.labelTimeIntervalHint = QLabel(self.pageTimeInterval)
        self.labelTimeIntervalHint.setObjectName(u"labelTimeIntervalHint")
        self.labelTimeIntervalHint.setWordWrap(True)

        self.verticalLayoutTimeInterval.addWidget(self.labelTimeIntervalHint)

        self.horizontalLayoutTimeInterval = QHBoxLayout()
        self.horizontalLayoutTimeInterval.setObjectName(u"horizontalLayoutTimeInterval")
        self.spinBoxIntervalValue = QSpinBox(self.pageTimeInterval)
        self.spinBoxIntervalValue.setObjectName(u"spinBoxIntervalValue")
        self.spinBoxIntervalValue.setMinimum(1)
        self.spinBoxIntervalValue.setMaximum(1000000)
        self.spinBoxIntervalValue.setValue(1)

        self.horizontalLayoutTimeInterval.addWidget(self.spinBoxIntervalValue)

        self.comboBoxIntervalUnit = QComboBox(self.pageTimeInterval)
        self.comboBoxIntervalUnit.setObjectName(u"comboBoxIntervalUnit")

        self.horizontalLayoutTimeInterval.addWidget(self.comboBoxIntervalUnit)

        self.horizontalSpacerTimeInterval = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutTimeInterval.addItem(self.horizontalSpacerTimeInterval)


        self.verticalLayoutTimeInterval.addLayout(self.horizontalLayoutTimeInterval)

        self.labelTimeIntervalCaloWarning = QLabel(self.pageTimeInterval)
        self.labelTimeIntervalCaloWarning.setObjectName(u"labelTimeIntervalCaloWarning")
        self.labelTimeIntervalCaloWarning.setWordWrap(True)

        self.verticalLayoutTimeInterval.addWidget(self.labelTimeIntervalCaloWarning)

        self.verticalSpacerTimeInterval = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutTimeInterval.addItem(self.verticalSpacerTimeInterval)

        self.stackedWidgetConfig.addWidget(self.pageTimeInterval)

        self.verticalLayout_5.addWidget(self.stackedWidgetConfig)


        self.horizontalLayout.addWidget(self.groupBoxConfig)


        self.verticalLayout_8.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(FactorsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_8.addWidget(self.buttonBox)


        self.retranslateUi(FactorsDialog)
        self.buttonBox.accepted.connect(FactorsDialog.accept)
        self.buttonBox.rejected.connect(FactorsDialog.reject)

        self.stackedWidgetConfig.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(FactorsDialog)
    # setupUi

    def retranslateUi(self, FactorsDialog):
        FactorsDialog.setWindowTitle(QCoreApplication.translate("FactorsDialog", u"Factors", None))
        self.groupBoxFactors.setTitle(QCoreApplication.translate("FactorsDialog", u"Factors", None))
        self.pushButtonAddFactor.setText(QCoreApplication.translate("FactorsDialog", u"Add Factor", None))
        self.pushButtonDeleteFactor.setText(QCoreApplication.translate("FactorsDialog", u"Delete Factor", None))
        self.groupBoxLevels.setTitle(QCoreApplication.translate("FactorsDialog", u"Levels", None))
        self.pushButtonAddLevel.setText(QCoreApplication.translate("FactorsDialog", u"Add Level", None))
        self.pushButtonDeleteLevel.setText(QCoreApplication.translate("FactorsDialog", u"Delete Level", None))
        self.pushButtonExtractLevels.setText(QCoreApplication.translate("FactorsDialog", u"Extract levels from...", None))
        self.groupBoxConfig.setTitle(QCoreApplication.translate("FactorsDialog", u"Configuration", None))
        self.labelAnimalsHint.setText(QCoreApplication.translate("FactorsDialog", u"Assign animals to the selected level:", None))
        self.labelCyclesHint.setText(QCoreApplication.translate("FactorsDialog", u"Light/Dark cycle boundaries:", None))
        self.labelLightCycleStart.setText(QCoreApplication.translate("FactorsDialog", u"Light cycle start", None))
        self.labelDarkCycleStart.setText(QCoreApplication.translate("FactorsDialog", u"Dark cycle start", None))
        self.labelPhasesHint.setText(QCoreApplication.translate("FactorsDialog", u"Phases (each phase becomes a level):", None))
#if QT_CONFIG(tooltip)
        self.toolButtonAddPhase.setToolTip(QCoreApplication.translate("FactorsDialog", u"Add phase", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButtonDeletePhase.setToolTip(QCoreApplication.translate("FactorsDialog", u"Delete selected phase", None))
#endif // QT_CONFIG(tooltip)
        self.labelAnimalPropertyHint.setText(QCoreApplication.translate("FactorsDialog", u"Animal property whose value defines the level for each animal:", None))
        self.labelColumnHint.setText(QCoreApplication.translate("FactorsDialog", u"Datatable column whose values define the factor levels:", None))
        self.labelTimeIntervalHint.setText(QCoreApplication.translate("FactorsDialog", u"Bin width. Each row is assigned an integer bin index (round(Timedelta / interval)) from experiment start.", None))
        self.labelTimeIntervalCaloWarning.setText("")
    # retranslateUi

