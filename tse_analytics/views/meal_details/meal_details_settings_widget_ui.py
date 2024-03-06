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
    QSpinBox, QVBoxLayout, QWidget)

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
        self.iterationsLabel = QLabel(self.groupBoxGeneralSettings)
        self.iterationsLabel.setObjectName(u"iterationsLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.iterationsLabel)

        self.iterationsSpinBox = QSpinBox(self.groupBoxGeneralSettings)
        self.iterationsSpinBox.setObjectName(u"iterationsSpinBox")
        self.iterationsSpinBox.setMaximum(1000000)
        self.iterationsSpinBox.setValue(10000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.iterationsSpinBox)

        self.predictionOffsetLabel = QLabel(self.groupBoxGeneralSettings)
        self.predictionOffsetLabel.setObjectName(u"predictionOffsetLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.predictionOffsetLabel)

        self.predictionOffsetSpinBox = QSpinBox(self.groupBoxGeneralSettings)
        self.predictionOffsetSpinBox.setObjectName(u"predictionOffsetSpinBox")
        self.predictionOffsetSpinBox.setValue(90)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.predictionOffsetSpinBox)

        self.flowLabel = QLabel(self.groupBoxGeneralSettings)
        self.flowLabel.setObjectName(u"flowLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.flowLabel)

        self.flowDoubleSpinBox = QDoubleSpinBox(self.groupBoxGeneralSettings)
        self.flowDoubleSpinBox.setObjectName(u"flowDoubleSpinBox")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.flowDoubleSpinBox)


        self.verticalLayout_2.addWidget(self.groupBoxGeneralSettings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(MealDetailsSettingsWidget)

        QMetaObject.connectSlotsByName(MealDetailsSettingsWidget)
    # setupUi

    def retranslateUi(self, MealDetailsSettingsWidget):
        MealDetailsSettingsWidget.setWindowTitle(QCoreApplication.translate("MealDetailsSettingsWidget", u"Form", None))
        self.groupBoxGeneralSettings.setTitle(QCoreApplication.translate("MealDetailsSettingsWidget", u"General", None))
        self.iterationsLabel.setText(QCoreApplication.translate("MealDetailsSettingsWidget", u"Iterations", None))
        self.predictionOffsetLabel.setText(QCoreApplication.translate("MealDetailsSettingsWidget", u"Prediction Offset", None))
        self.flowLabel.setText(QCoreApplication.translate("MealDetailsSettingsWidget", u"Flow [l/min]", None))
    # retranslateUi

