# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calo_details_gas_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QGroupBox, QHBoxLayout,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_CaloDetailsGasSettingsWidget(object):
    def setupUi(self, CaloDetailsGasSettingsWidget):
        if not CaloDetailsGasSettingsWidget.objectName():
            CaloDetailsGasSettingsWidget.setObjectName(u"CaloDetailsGasSettingsWidget")
        CaloDetailsGasSettingsWidget.resize(460, 832)
        self.verticalLayout = QVBoxLayout(CaloDetailsGasSettingsWidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.titleGroupBox = QGroupBox(CaloDetailsGasSettingsWidget)
        self.titleGroupBox.setObjectName(u"titleGroupBox")
        self.verticalLayout_2 = QVBoxLayout(self.titleGroupBox)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.trainingIntervalGroupBox = QGroupBox(self.titleGroupBox)
        self.trainingIntervalGroupBox.setObjectName(u"trainingIntervalGroupBox")
        self.horizontalLayout = QHBoxLayout(self.trainingIntervalGroupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.spinBoxStartOffset = QSpinBox(self.trainingIntervalGroupBox)
        self.spinBoxStartOffset.setObjectName(u"spinBoxStartOffset")
        self.spinBoxStartOffset.setValue(20)

        self.horizontalLayout.addWidget(self.spinBoxStartOffset)

        self.spinBoxEndOffset = QSpinBox(self.trainingIntervalGroupBox)
        self.spinBoxEndOffset.setObjectName(u"spinBoxEndOffset")
        self.spinBoxEndOffset.setValue(30)

        self.horizontalLayout.addWidget(self.spinBoxEndOffset)


        self.verticalLayout_2.addWidget(self.trainingIntervalGroupBox)


        self.verticalLayout.addWidget(self.titleGroupBox)

        self.tabWidget = QTabWidget(CaloDetailsGasSettingsWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabBounds = QWidget()
        self.tabBounds.setObjectName(u"tabBounds")
        self.verticalLayout_3 = QVBoxLayout(self.tabBounds)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(2, 2, 2, 2)
        self.groupBoxA = QGroupBox(self.tabBounds)
        self.groupBoxA.setObjectName(u"groupBoxA")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxA)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.doubleSpinBoxMinA = QDoubleSpinBox(self.groupBoxA)
        self.doubleSpinBoxMinA.setObjectName(u"doubleSpinBoxMinA")
        self.doubleSpinBoxMinA.setDecimals(15)

        self.horizontalLayout_2.addWidget(self.doubleSpinBoxMinA)

        self.doubleSpinBoxMaxA = QDoubleSpinBox(self.groupBoxA)
        self.doubleSpinBoxMaxA.setObjectName(u"doubleSpinBoxMaxA")
        self.doubleSpinBoxMaxA.setDecimals(15)

        self.horizontalLayout_2.addWidget(self.doubleSpinBoxMaxA)


        self.verticalLayout_3.addWidget(self.groupBoxA)

        self.groupBoxB = QGroupBox(self.tabBounds)
        self.groupBoxB.setObjectName(u"groupBoxB")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBoxB)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.doubleSpinBoxMinB = QDoubleSpinBox(self.groupBoxB)
        self.doubleSpinBoxMinB.setObjectName(u"doubleSpinBoxMinB")
        self.doubleSpinBoxMinB.setDecimals(15)

        self.horizontalLayout_3.addWidget(self.doubleSpinBoxMinB)

        self.doubleSpinBoxMaxB = QDoubleSpinBox(self.groupBoxB)
        self.doubleSpinBoxMaxB.setObjectName(u"doubleSpinBoxMaxB")
        self.doubleSpinBoxMaxB.setDecimals(15)

        self.horizontalLayout_3.addWidget(self.doubleSpinBoxMaxB)


        self.verticalLayout_3.addWidget(self.groupBoxB)

        self.groupBoxC = QGroupBox(self.tabBounds)
        self.groupBoxC.setObjectName(u"groupBoxC")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBoxC)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.doubleSpinBoxMinC = QDoubleSpinBox(self.groupBoxC)
        self.doubleSpinBoxMinC.setObjectName(u"doubleSpinBoxMinC")
        self.doubleSpinBoxMinC.setDecimals(15)

        self.horizontalLayout_4.addWidget(self.doubleSpinBoxMinC)

        self.doubleSpinBoxMaxC = QDoubleSpinBox(self.groupBoxC)
        self.doubleSpinBoxMaxC.setObjectName(u"doubleSpinBoxMaxC")
        self.doubleSpinBoxMaxC.setDecimals(15)

        self.horizontalLayout_4.addWidget(self.doubleSpinBoxMaxC)


        self.verticalLayout_3.addWidget(self.groupBoxC)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tabBounds, "")
        self.tabRefBounds = QWidget()
        self.tabRefBounds.setObjectName(u"tabRefBounds")
        self.verticalLayout_4 = QVBoxLayout(self.tabRefBounds)
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(2, 2, 2, 2)
        self.groupBoxRefA = QGroupBox(self.tabRefBounds)
        self.groupBoxRefA.setObjectName(u"groupBoxRefA")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBoxRefA)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.doubleSpinBoxRefMinA = QDoubleSpinBox(self.groupBoxRefA)
        self.doubleSpinBoxRefMinA.setObjectName(u"doubleSpinBoxRefMinA")
        self.doubleSpinBoxRefMinA.setDecimals(15)

        self.horizontalLayout_7.addWidget(self.doubleSpinBoxRefMinA)

        self.doubleSpinBoxRefMaxA = QDoubleSpinBox(self.groupBoxRefA)
        self.doubleSpinBoxRefMaxA.setObjectName(u"doubleSpinBoxRefMaxA")
        self.doubleSpinBoxRefMaxA.setDecimals(15)

        self.horizontalLayout_7.addWidget(self.doubleSpinBoxRefMaxA)


        self.verticalLayout_4.addWidget(self.groupBoxRefA)

        self.groupBoxRefB = QGroupBox(self.tabRefBounds)
        self.groupBoxRefB.setObjectName(u"groupBoxRefB")
        self.horizontalLayout_5 = QHBoxLayout(self.groupBoxRefB)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.doubleSpinBoxRefMinB = QDoubleSpinBox(self.groupBoxRefB)
        self.doubleSpinBoxRefMinB.setObjectName(u"doubleSpinBoxRefMinB")
        self.doubleSpinBoxRefMinB.setDecimals(15)

        self.horizontalLayout_5.addWidget(self.doubleSpinBoxRefMinB)

        self.doubleSpinBoxRefMaxB = QDoubleSpinBox(self.groupBoxRefB)
        self.doubleSpinBoxRefMaxB.setObjectName(u"doubleSpinBoxRefMaxB")
        self.doubleSpinBoxRefMaxB.setDecimals(15)

        self.horizontalLayout_5.addWidget(self.doubleSpinBoxRefMaxB)


        self.verticalLayout_4.addWidget(self.groupBoxRefB)

        self.groupBoxRefC = QGroupBox(self.tabRefBounds)
        self.groupBoxRefC.setObjectName(u"groupBoxRefC")
        self.horizontalLayout_6 = QHBoxLayout(self.groupBoxRefC)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.doubleSpinBoxRefMinC = QDoubleSpinBox(self.groupBoxRefC)
        self.doubleSpinBoxRefMinC.setObjectName(u"doubleSpinBoxRefMinC")
        self.doubleSpinBoxRefMinC.setDecimals(15)

        self.horizontalLayout_6.addWidget(self.doubleSpinBoxRefMinC)

        self.doubleSpinBoxRefMaxC = QDoubleSpinBox(self.groupBoxRefC)
        self.doubleSpinBoxRefMaxC.setObjectName(u"doubleSpinBoxRefMaxC")
        self.doubleSpinBoxRefMaxC.setDecimals(15)

        self.horizontalLayout_6.addWidget(self.doubleSpinBoxRefMaxC)


        self.verticalLayout_4.addWidget(self.groupBoxRefC)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tabRefBounds, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(CaloDetailsGasSettingsWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(CaloDetailsGasSettingsWidget)
    # setupUi

    def retranslateUi(self, CaloDetailsGasSettingsWidget):
        CaloDetailsGasSettingsWidget.setWindowTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"Form", None))
        self.titleGroupBox.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"[Gas Name]", None))
        self.trainingIntervalGroupBox.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"Training Interval", None))
        self.groupBoxA.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"a", None))
        self.groupBoxB.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"b", None))
        self.groupBoxC.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"C", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBounds), QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"Bounds", None))
        self.groupBoxRefA.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"a", None))
        self.groupBoxRefB.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"b", None))
        self.groupBoxRefC.setTitle(QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"C", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabRefBounds), QCoreApplication.translate("CaloDetailsGasSettingsWidget", u"Reference Bounds", None))
    # retranslateUi

