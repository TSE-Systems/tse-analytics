# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'outliers_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QGroupBox, QHBoxLayout,
    QPushButton, QRadioButton, QSizePolicy, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_OutliersWidget(object):
    def setupUi(self, OutliersWidget):
        if not OutliersWidget.objectName():
            OutliersWidget.setObjectName(u"OutliersWidget")
        self.verticalLayout = QVBoxLayout(OutliersWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxMode = QGroupBox(OutliersWidget)
        self.groupBoxMode.setObjectName(u"groupBoxMode")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxMode)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.radioButtonDetectionOff = QRadioButton(self.groupBoxMode)
        self.radioButtonDetectionOff.setObjectName(u"radioButtonDetectionOff")

        self.verticalLayout_6.addWidget(self.radioButtonDetectionOff)

        self.radioButtonHighlightOutliers = QRadioButton(self.groupBoxMode)
        self.radioButtonHighlightOutliers.setObjectName(u"radioButtonHighlightOutliers")

        self.verticalLayout_6.addWidget(self.radioButtonHighlightOutliers)

        self.radioButtonRemoveOutliers = QRadioButton(self.groupBoxMode)
        self.radioButtonRemoveOutliers.setObjectName(u"radioButtonRemoveOutliers")

        self.verticalLayout_6.addWidget(self.radioButtonRemoveOutliers)


        self.verticalLayout.addWidget(self.groupBoxMode)

        self.groupBoxDetectionType = QGroupBox(OutliersWidget)
        self.groupBoxDetectionType.setObjectName(u"groupBoxDetectionType")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxDetectionType)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.radioButtonIqr = QRadioButton(self.groupBoxDetectionType)
        self.radioButtonIqr.setObjectName(u"radioButtonIqr")

        self.verticalLayout_2.addWidget(self.radioButtonIqr)

        self.radioButtonZScore = QRadioButton(self.groupBoxDetectionType)
        self.radioButtonZScore.setObjectName(u"radioButtonZScore")

        self.verticalLayout_2.addWidget(self.radioButtonZScore)

        self.radioButtonThresholds = QRadioButton(self.groupBoxDetectionType)
        self.radioButtonThresholds.setObjectName(u"radioButtonThresholds")

        self.verticalLayout_2.addWidget(self.radioButtonThresholds)


        self.verticalLayout.addWidget(self.groupBoxDetectionType)

        self.groupBoxIqrMultiplier = QGroupBox(OutliersWidget)
        self.groupBoxIqrMultiplier.setObjectName(u"groupBoxIqrMultiplier")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxIqrMultiplier)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.doubleSpinBoxIqrMultiplier = QDoubleSpinBox(self.groupBoxIqrMultiplier)
        self.doubleSpinBoxIqrMultiplier.setObjectName(u"doubleSpinBoxIqrMultiplier")

        self.verticalLayout_3.addWidget(self.doubleSpinBoxIqrMultiplier)


        self.verticalLayout.addWidget(self.groupBoxIqrMultiplier)

        self.groupBoxMinThreshold = QGroupBox(OutliersWidget)
        self.groupBoxMinThreshold.setObjectName(u"groupBoxMinThreshold")
        self.groupBoxMinThreshold.setCheckable(True)
        self.groupBoxMinThreshold.setChecked(False)
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxMinThreshold)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.doubleSpinBoxMinThreshold = QDoubleSpinBox(self.groupBoxMinThreshold)
        self.doubleSpinBoxMinThreshold.setObjectName(u"doubleSpinBoxMinThreshold")
        self.doubleSpinBoxMinThreshold.setDecimals(3)
        self.doubleSpinBoxMinThreshold.setMinimum(-999999999999999.000000000000000)
        self.doubleSpinBoxMinThreshold.setMaximum(999999999999999.000000000000000)

        self.verticalLayout_4.addWidget(self.doubleSpinBoxMinThreshold)


        self.verticalLayout.addWidget(self.groupBoxMinThreshold)

        self.groupBoxMaxThreshold = QGroupBox(OutliersWidget)
        self.groupBoxMaxThreshold.setObjectName(u"groupBoxMaxThreshold")
        self.groupBoxMaxThreshold.setCheckable(True)
        self.groupBoxMaxThreshold.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxMaxThreshold)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.doubleSpinBoxMaxThreshold = QDoubleSpinBox(self.groupBoxMaxThreshold)
        self.doubleSpinBoxMaxThreshold.setObjectName(u"doubleSpinBoxMaxThreshold")
        self.doubleSpinBoxMaxThreshold.setDecimals(3)
        self.doubleSpinBoxMaxThreshold.setMinimum(-999999999999999.000000000000000)
        self.doubleSpinBoxMaxThreshold.setMaximum(999999999999999.000000000000000)

        self.verticalLayout_5.addWidget(self.doubleSpinBoxMaxThreshold)


        self.verticalLayout.addWidget(self.groupBoxMaxThreshold)

        self.widget = QWidget(OutliersWidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButtonFreezeRemoval = QPushButton(self.widget)
        self.pushButtonFreezeRemoval.setObjectName(u"pushButtonFreezeRemoval")

        self.horizontalLayout.addWidget(self.pushButtonFreezeRemoval)


        self.verticalLayout.addWidget(self.widget)


        self.retranslateUi(OutliersWidget)

        QMetaObject.connectSlotsByName(OutliersWidget)
    # setupUi

    def retranslateUi(self, OutliersWidget):
        self.groupBoxMode.setTitle(QCoreApplication.translate("OutliersWidget", u"Mode", None))
        self.radioButtonDetectionOff.setText(QCoreApplication.translate("OutliersWidget", u"Outliers detection off", None))
        self.radioButtonHighlightOutliers.setText(QCoreApplication.translate("OutliersWidget", u"Highlight outliers", None))
        self.radioButtonRemoveOutliers.setText(QCoreApplication.translate("OutliersWidget", u"Remove outliers", None))
        self.groupBoxDetectionType.setTitle(QCoreApplication.translate("OutliersWidget", u"Detection Type", None))
        self.radioButtonIqr.setText(QCoreApplication.translate("OutliersWidget", u"Interquartile Range (IQR)", None))
        self.radioButtonZScore.setText(QCoreApplication.translate("OutliersWidget", u"Z-Score", None))
        self.radioButtonThresholds.setText(QCoreApplication.translate("OutliersWidget", u"Thresholds", None))
        self.groupBoxIqrMultiplier.setTitle(QCoreApplication.translate("OutliersWidget", u"IQR Multiplier", None))
        self.groupBoxMinThreshold.setTitle(QCoreApplication.translate("OutliersWidget", u"Min Threshold", None))
        self.groupBoxMaxThreshold.setTitle(QCoreApplication.translate("OutliersWidget", u"Max Threshold", None))
        self.pushButtonFreezeRemoval.setText(QCoreApplication.translate("OutliersWidget", u"Freeze Outliers Removal", None))
        pass
    # retranslateUi

