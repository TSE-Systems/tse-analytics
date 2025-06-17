# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'drinkfeed_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTableView, QTimeEdit, QToolButton,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_DrinkFeedSettingsWidget(object):
    def setupUi(self, DrinkFeedSettingsWidget):
        if not DrinkFeedSettingsWidget.objectName():
            DrinkFeedSettingsWidget.setObjectName(u"DrinkFeedSettingsWidget")
        self.verticalLayout = QVBoxLayout(DrinkFeedSettingsWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.scrollArea = QScrollArea(DrinkFeedSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 277, 457))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.groupBoxAnalysisType = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxAnalysisType.setObjectName(u"groupBoxAnalysisType")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxAnalysisType)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButtonSequentialType = QRadioButton(self.groupBoxAnalysisType)
        self.radioButtonSequentialType.setObjectName(u"radioButtonSequentialType")
        self.radioButtonSequentialType.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButtonSequentialType)

        self.radioButtonIntervalType = QRadioButton(self.groupBoxAnalysisType)
        self.radioButtonIntervalType.setObjectName(u"radioButtonIntervalType")

        self.verticalLayout_3.addWidget(self.radioButtonIntervalType)


        self.verticalLayout_2.addWidget(self.groupBoxAnalysisType)

        self.groupBoxSequentialSettings = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxSequentialSettings.setObjectName(u"groupBoxSequentialSettings")
        self.formLayout = QFormLayout(self.groupBoxSequentialSettings)
        self.formLayout.setObjectName(u"formLayout")
        self.intermealIntervalLabel = QLabel(self.groupBoxSequentialSettings)
        self.intermealIntervalLabel.setObjectName(u"intermealIntervalLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.intermealIntervalLabel)

        self.intermealIntervalTimeEdit = QTimeEdit(self.groupBoxSequentialSettings)
        self.intermealIntervalTimeEdit.setObjectName(u"intermealIntervalTimeEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.intermealIntervalTimeEdit)

        self.drinkingMinimumAmountLabel = QLabel(self.groupBoxSequentialSettings)
        self.drinkingMinimumAmountLabel.setObjectName(u"drinkingMinimumAmountLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.drinkingMinimumAmountLabel)

        self.drinkingMinimumAmountDoubleSpinBox = QDoubleSpinBox(self.groupBoxSequentialSettings)
        self.drinkingMinimumAmountDoubleSpinBox.setObjectName(u"drinkingMinimumAmountDoubleSpinBox")
        self.drinkingMinimumAmountDoubleSpinBox.setDecimals(3)
        self.drinkingMinimumAmountDoubleSpinBox.setSingleStep(0.001000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.drinkingMinimumAmountDoubleSpinBox)

        self.feedingMinimumAmountLabel = QLabel(self.groupBoxSequentialSettings)
        self.feedingMinimumAmountLabel.setObjectName(u"feedingMinimumAmountLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.feedingMinimumAmountLabel)

        self.feedingMinimumAmountDoubleSpinBox = QDoubleSpinBox(self.groupBoxSequentialSettings)
        self.feedingMinimumAmountDoubleSpinBox.setObjectName(u"feedingMinimumAmountDoubleSpinBox")
        self.feedingMinimumAmountDoubleSpinBox.setDecimals(3)
        self.feedingMinimumAmountDoubleSpinBox.setSingleStep(0.001000000000000)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.feedingMinimumAmountDoubleSpinBox)


        self.verticalLayout_2.addWidget(self.groupBoxSequentialSettings)

        self.groupBoxIntervalSettings = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxIntervalSettings.setObjectName(u"groupBoxIntervalSettings")
        self.formLayout_2 = QFormLayout(self.groupBoxIntervalSettings)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.fixedIntervalLabel = QLabel(self.groupBoxIntervalSettings)
        self.fixedIntervalLabel.setObjectName(u"fixedIntervalLabel")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.fixedIntervalLabel)

        self.fixedIntervalTimeEdit = QTimeEdit(self.groupBoxIntervalSettings)
        self.fixedIntervalTimeEdit.setObjectName(u"fixedIntervalTimeEdit")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fixedIntervalTimeEdit)


        self.verticalLayout_2.addWidget(self.groupBoxIntervalSettings)

        self.groupBoxDiets = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxDiets.setObjectName(u"groupBoxDiets")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxDiets)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tableViewDiets = QTableView(self.groupBoxDiets)
        self.tableViewDiets.setObjectName(u"tableViewDiets")
        self.tableViewDiets.verticalHeader().setDefaultSectionSize(24)

        self.verticalLayout_4.addWidget(self.tableViewDiets)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAddDiet = QToolButton(self.groupBoxDiets)
        self.toolButtonAddDiet.setObjectName(u"toolButtonAddDiet")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-add-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonAddDiet.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonAddDiet)

        self.toolButtonDeleteDiet = QToolButton(self.groupBoxDiets)
        self.toolButtonDeleteDiet.setObjectName(u"toolButtonDeleteDiet")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-minus-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonDeleteDiet.setIcon(icon1)

        self.horizontalLayout.addWidget(self.toolButtonDeleteDiet)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addWidget(self.groupBoxDiets)

        self.pushButtonResetSettings = QPushButton(self.scrollAreaWidgetContents)
        self.pushButtonResetSettings.setObjectName(u"pushButtonResetSettings")

        self.verticalLayout_2.addWidget(self.pushButtonResetSettings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(DrinkFeedSettingsWidget)

        QMetaObject.connectSlotsByName(DrinkFeedSettingsWidget)
    # setupUi

    def retranslateUi(self, DrinkFeedSettingsWidget):
        self.groupBoxAnalysisType.setTitle(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Analysis Type", None))
        self.radioButtonSequentialType.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Sequential", None))
        self.radioButtonIntervalType.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Interval", None))
        self.groupBoxSequentialSettings.setTitle(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Sequential Analysis", None))
        self.intermealIntervalLabel.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Inter-meal Interval [hh:mm:ss]", None))
        self.intermealIntervalTimeEdit.setDisplayFormat(QCoreApplication.translate("DrinkFeedSettingsWidget", u"HH:mm:ss", None))
        self.drinkingMinimumAmountLabel.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Drinking Minimum Amount [ml]", None))
        self.feedingMinimumAmountLabel.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Feeding Minimum Amount [g]", None))
        self.groupBoxIntervalSettings.setTitle(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Interval Analysis", None))
        self.fixedIntervalLabel.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Fixed Interval [hh:mm:ss]", None))
        self.fixedIntervalTimeEdit.setDisplayFormat(QCoreApplication.translate("DrinkFeedSettingsWidget", u"HH:mm:ss", None))
        self.groupBoxDiets.setTitle(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Diets", None))
#if QT_CONFIG(tooltip)
        self.toolButtonAddDiet.setToolTip(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Add diet", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButtonDeleteDiet.setToolTip(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Delete selected diet", None))
#endif // QT_CONFIG(tooltip)
        self.pushButtonResetSettings.setText(QCoreApplication.translate("DrinkFeedSettingsWidget", u"Reset Settings", None))
        pass
    # retranslateUi

