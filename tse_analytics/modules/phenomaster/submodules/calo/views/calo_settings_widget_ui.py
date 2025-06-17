# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_settings_widget.ui'
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
    QGroupBox, QLabel, QScrollArea, QSizePolicy,
    QSpinBox, QVBoxLayout, QWidget)

from tse_analytics.modules.phenomaster.submodules.calo.views.calo_gas_settings_widget import CaloGasSettingsWidget

class Ui_CaloSettingsWidget(object):
    def setupUi(self, CaloSettingsWidget):
        if not CaloSettingsWidget.objectName():
            CaloSettingsWidget.setObjectName(u"CaloSettingsWidget")
        self.verticalLayout = QVBoxLayout(CaloSettingsWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.scrollArea = QScrollArea(CaloSettingsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 193, 205))
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

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.iterationsLabel)

        self.iterationsSpinBox = QSpinBox(self.groupBoxGeneralSettings)
        self.iterationsSpinBox.setObjectName(u"iterationsSpinBox")
        self.iterationsSpinBox.setMaximum(1000000)
        self.iterationsSpinBox.setValue(10000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.iterationsSpinBox)

        self.predictionOffsetLabel = QLabel(self.groupBoxGeneralSettings)
        self.predictionOffsetLabel.setObjectName(u"predictionOffsetLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.predictionOffsetLabel)

        self.predictionOffsetSpinBox = QSpinBox(self.groupBoxGeneralSettings)
        self.predictionOffsetSpinBox.setObjectName(u"predictionOffsetSpinBox")
        self.predictionOffsetSpinBox.setValue(90)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.predictionOffsetSpinBox)

        self.flowLabel = QLabel(self.groupBoxGeneralSettings)
        self.flowLabel.setObjectName(u"flowLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.flowLabel)

        self.flowDoubleSpinBox = QDoubleSpinBox(self.groupBoxGeneralSettings)
        self.flowDoubleSpinBox.setObjectName(u"flowDoubleSpinBox")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.flowDoubleSpinBox)


        self.verticalLayout_2.addWidget(self.groupBoxGeneralSettings)

        self.groupBoxGasSettings = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxGasSettings.setObjectName(u"groupBoxGasSettings")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxGasSettings.sizePolicy().hasHeightForWidth())
        self.groupBoxGasSettings.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxGasSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widgetO2Settings = CaloGasSettingsWidget(self.groupBoxGasSettings)
        self.widgetO2Settings.setObjectName(u"widgetO2Settings")

        self.verticalLayout_3.addWidget(self.widgetO2Settings)

        self.widgetCO2Settings = CaloGasSettingsWidget(self.groupBoxGasSettings)
        self.widgetCO2Settings.setObjectName(u"widgetCO2Settings")

        self.verticalLayout_3.addWidget(self.widgetCO2Settings)


        self.verticalLayout_2.addWidget(self.groupBoxGasSettings)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(CaloSettingsWidget)

        QMetaObject.connectSlotsByName(CaloSettingsWidget)
    # setupUi

    def retranslateUi(self, CaloSettingsWidget):
        self.groupBoxGeneralSettings.setTitle(QCoreApplication.translate("CaloSettingsWidget", u"General", None))
        self.iterationsLabel.setText(QCoreApplication.translate("CaloSettingsWidget", u"Iterations", None))
        self.predictionOffsetLabel.setText(QCoreApplication.translate("CaloSettingsWidget", u"Prediction Offset", None))
        self.flowLabel.setText(QCoreApplication.translate("CaloSettingsWidget", u"Flow [l/min]", None))
        self.groupBoxGasSettings.setTitle(QCoreApplication.translate("CaloSettingsWidget", u"Gas Settings", None))
        pass
    # retranslateUi

