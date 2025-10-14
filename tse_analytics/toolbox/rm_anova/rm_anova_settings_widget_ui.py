# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rm_anova_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QSizePolicy,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_RMAnovaSettingsWidget(object):
    def setupUi(self, RMAnovaSettingsWidget):
        if not RMAnovaSettingsWidget.objectName():
            RMAnovaSettingsWidget.setObjectName(u"RMAnovaSettingsWidget")
        self.verticalLayout = QVBoxLayout(RMAnovaSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxPAdjustment = QGroupBox(RMAnovaSettingsWidget)
        self.groupBoxPAdjustment.setObjectName(u"groupBoxPAdjustment")
        self.verticalLayout_7 = QVBoxLayout(self.groupBoxPAdjustment)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.comboBoxPAdjustment = QComboBox(self.groupBoxPAdjustment)
        self.comboBoxPAdjustment.setObjectName(u"comboBoxPAdjustment")

        self.verticalLayout_7.addWidget(self.comboBoxPAdjustment)


        self.verticalLayout.addWidget(self.groupBoxPAdjustment)

        self.groupBoxEffectSizeType = QGroupBox(RMAnovaSettingsWidget)
        self.groupBoxEffectSizeType.setObjectName(u"groupBoxEffectSizeType")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxEffectSizeType)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.comboBoxEffectSizeType = QComboBox(self.groupBoxEffectSizeType)
        self.comboBoxEffectSizeType.setObjectName(u"comboBoxEffectSizeType")

        self.verticalLayout_6.addWidget(self.comboBoxEffectSizeType)


        self.verticalLayout.addWidget(self.groupBoxEffectSizeType)


        self.retranslateUi(RMAnovaSettingsWidget)

        QMetaObject.connectSlotsByName(RMAnovaSettingsWidget)
    # setupUi

    def retranslateUi(self, RMAnovaSettingsWidget):
        self.groupBoxPAdjustment.setTitle(QCoreApplication.translate("RMAnovaSettingsWidget", u"P-values adjustment", None))
        self.groupBoxEffectSizeType.setTitle(QCoreApplication.translate("RMAnovaSettingsWidget", u"Effect size type", None))
        pass
    # retranslateUi

