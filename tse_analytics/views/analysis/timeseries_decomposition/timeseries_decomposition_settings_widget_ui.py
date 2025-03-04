# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'timeseries_decomposition_settings_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QRadioButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_TimeseriesDecompositionSettingsWidget(object):
    def setupUi(self, TimeseriesDecompositionSettingsWidget):
        if not TimeseriesDecompositionSettingsWidget.objectName():
            TimeseriesDecompositionSettingsWidget.setObjectName(u"TimeseriesDecompositionSettingsWidget")
        self.verticalLayout = QVBoxLayout(TimeseriesDecompositionSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxMethod = QGroupBox(TimeseriesDecompositionSettingsWidget)
        self.groupBoxMethod.setObjectName(u"groupBoxMethod")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxMethod)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButtonMethodNaive = QRadioButton(self.groupBoxMethod)
        self.radioButtonMethodNaive.setObjectName(u"radioButtonMethodNaive")
        self.radioButtonMethodNaive.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButtonMethodNaive)

        self.radioButtonMethodSTL = QRadioButton(self.groupBoxMethod)
        self.radioButtonMethodSTL.setObjectName(u"radioButtonMethodSTL")

        self.verticalLayout_3.addWidget(self.radioButtonMethodSTL)

        self.radioButtonMethodMSTL = QRadioButton(self.groupBoxMethod)
        self.radioButtonMethodMSTL.setObjectName(u"radioButtonMethodMSTL")

        self.verticalLayout_3.addWidget(self.radioButtonMethodMSTL)


        self.verticalLayout.addWidget(self.groupBoxMethod)

        self.groupBoxModel = QGroupBox(TimeseriesDecompositionSettingsWidget)
        self.groupBoxModel.setObjectName(u"groupBoxModel")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxModel)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.radioButtonModelAdditive = QRadioButton(self.groupBoxModel)
        self.radioButtonModelAdditive.setObjectName(u"radioButtonModelAdditive")
        self.radioButtonModelAdditive.setChecked(True)

        self.verticalLayout_2.addWidget(self.radioButtonModelAdditive)

        self.radioButtonModelMultiplicative = QRadioButton(self.groupBoxModel)
        self.radioButtonModelMultiplicative.setObjectName(u"radioButtonModelMultiplicative")

        self.verticalLayout_2.addWidget(self.radioButtonModelMultiplicative)


        self.verticalLayout.addWidget(self.groupBoxModel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.periodLabel = QLabel(TimeseriesDecompositionSettingsWidget)
        self.periodLabel.setObjectName(u"periodLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.periodLabel)

        self.periodSpinBox = QSpinBox(TimeseriesDecompositionSettingsWidget)
        self.periodSpinBox.setObjectName(u"periodSpinBox")
        self.periodSpinBox.setMaximum(1000000000)
        self.periodSpinBox.setValue(365)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.periodSpinBox)


        self.verticalLayout.addLayout(self.formLayout)


        self.retranslateUi(TimeseriesDecompositionSettingsWidget)

        QMetaObject.connectSlotsByName(TimeseriesDecompositionSettingsWidget)
    # setupUi

    def retranslateUi(self, TimeseriesDecompositionSettingsWidget):
        self.groupBoxMethod.setTitle(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Method", None))
#if QT_CONFIG(tooltip)
        self.radioButtonMethodNaive.setToolTip(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Seasonal decomposition using moving averages", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonMethodNaive.setText(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Naive", None))
#if QT_CONFIG(tooltip)
        self.radioButtonMethodSTL.setToolTip(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Season-Trend decomposition using LOESS", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonMethodSTL.setText(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"STL", None))
#if QT_CONFIG(tooltip)
        self.radioButtonMethodMSTL.setToolTip(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Multiple Seasonal-Trend decomposition using LOESS", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonMethodMSTL.setText(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"MSTL", None))
        self.groupBoxModel.setTitle(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Model", None))
        self.radioButtonModelAdditive.setText(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Additive", None))
        self.radioButtonModelMultiplicative.setText(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Multiplicative", None))
        self.periodLabel.setText(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Period", None))
#if QT_CONFIG(tooltip)
        self.periodSpinBox.setToolTip(QCoreApplication.translate("TimeseriesDecompositionSettingsWidget", u"Period of the series (eg, 1 for annual, 4 for quarterly, etc)", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

