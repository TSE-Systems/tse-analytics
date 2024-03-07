# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'meal_details_settings_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QFrame,
    QGroupBox, QLabel, QScrollArea, QSizePolicy,
    QTimeEdit, QVBoxLayout, QWidget)

class Ui_MealDetailsSettingsWidget(object):
    def setupUi(self, MealDetailsSettingsWidget):
        if not MealDetailsSettingsWidget.objectName():
            MealDetailsSettingsWidget.setObjectName(u"MealDetailsSettingsWidget")
        MealDetailsSettingsWidget.resize(546, 585)
        self.verticalLayout = QVBoxLayout(MealDetailsSettingsWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.scrollArea = QScrollArea(MealDetailsSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 538, 577))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.groupBoxGeneralSettings = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxGeneralSettings.setObjectName(u"groupBoxGeneralSettings")
        self.formLayout = QFormLayout(self.groupBoxGeneralSettings)
        self.formLayout.setObjectName(u"formLayout")
        self.intermealIntervalLabel = QLabel(self.groupBoxGeneralSettings)
        self.intermealIntervalLabel.setObjectName(u"intermealIntervalLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.intermealIntervalLabel)

        self.intermealIntervalTimeEdit = QTimeEdit(self.groupBoxGeneralSettings)
        self.intermealIntervalTimeEdit.setObjectName(u"intermealIntervalTimeEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.intermealIntervalTimeEdit)

        self.drinkingMinimumAmountLabel = QLabel(self.groupBoxGeneralSettings)
        self.drinkingMinimumAmountLabel.setObjectName(u"drinkingMinimumAmountLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.drinkingMinimumAmountLabel)

        self.drinkingMinimumAmountDoubleSpinBox = QDoubleSpinBox(self.groupBoxGeneralSettings)
        self.drinkingMinimumAmountDoubleSpinBox.setObjectName(u"drinkingMinimumAmountDoubleSpinBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.drinkingMinimumAmountDoubleSpinBox)

        self.feedingMinimumAmountLabel = QLabel(self.groupBoxGeneralSettings)
        self.feedingMinimumAmountLabel.setObjectName(u"feedingMinimumAmountLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.feedingMinimumAmountLabel)

        self.feedingMinimumAmountDoubleSpinBox = QDoubleSpinBox(self.groupBoxGeneralSettings)
        self.feedingMinimumAmountDoubleSpinBox.setObjectName(u"feedingMinimumAmountDoubleSpinBox")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.feedingMinimumAmountDoubleSpinBox)


        self.verticalLayout_2.addWidget(self.groupBoxGeneralSettings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(MealDetailsSettingsWidget)

        QMetaObject.connectSlotsByName(MealDetailsSettingsWidget)
    # setupUi

    def retranslateUi(self, MealDetailsSettingsWidget):
        MealDetailsSettingsWidget.setWindowTitle(QCoreApplication.translate("MealDetailsSettingsWidget", u"Form", None))
        self.groupBoxGeneralSettings.setTitle(QCoreApplication.translate("MealDetailsSettingsWidget", u"General", None))
        self.intermealIntervalLabel.setText(QCoreApplication.translate("MealDetailsSettingsWidget", u"Intermeal Interval [hh:mm:ss]", None))
        self.intermealIntervalTimeEdit.setDisplayFormat(QCoreApplication.translate("MealDetailsSettingsWidget", u"HH:mm:ss", None))
        self.drinkingMinimumAmountLabel.setText(QCoreApplication.translate("MealDetailsSettingsWidget", u"Drinking Minimum Amount [ml]", None))
        self.feedingMinimumAmountLabel.setText(QCoreApplication.translate("MealDetailsSettingsWidget", u"Feeding Minimum Amount [g]", None))
    # retranslateUi

