# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'decomposition_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QRadioButton, QSizePolicy, QSpacerItem,
    QSpinBox, QSplitter, QToolButton, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
import resources_rc

class Ui_DecompositionWidget(object):
    def setupUi(self, DecompositionWidget):
        if not DecompositionWidget.objectName():
            DecompositionWidget.setObjectName(u"DecompositionWidget")
        DecompositionWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(DecompositionWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(DecompositionWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(DecompositionWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(DecompositionWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.canvas = MplCanvas(self.splitter)
        self.canvas.setObjectName(u"canvas")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy1)
        self.splitter.addWidget(self.canvas)
        self.groupBoxSettings = QGroupBox(self.splitter)
        self.groupBoxSettings.setObjectName(u"groupBoxSettings")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxSettings)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBoxMethod = QGroupBox(self.groupBoxSettings)
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


        self.verticalLayout_6.addWidget(self.groupBoxMethod)

        self.groupBoxModel = QGroupBox(self.groupBoxSettings)
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


        self.verticalLayout_6.addWidget(self.groupBoxModel)

        self.groupBoxFrequency = QGroupBox(self.groupBoxSettings)
        self.groupBoxFrequency.setObjectName(u"groupBoxFrequency")
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxFrequency)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.radioButtonDayFrequency = QRadioButton(self.groupBoxFrequency)
        self.radioButtonDayFrequency.setObjectName(u"radioButtonDayFrequency")

        self.verticalLayout_5.addWidget(self.radioButtonDayFrequency)

        self.radioButtonHourFrequency = QRadioButton(self.groupBoxFrequency)
        self.radioButtonHourFrequency.setObjectName(u"radioButtonHourFrequency")

        self.verticalLayout_5.addWidget(self.radioButtonHourFrequency)

        self.radioButtonMinuteFrequency = QRadioButton(self.groupBoxFrequency)
        self.radioButtonMinuteFrequency.setObjectName(u"radioButtonMinuteFrequency")
        self.radioButtonMinuteFrequency.setChecked(True)

        self.verticalLayout_5.addWidget(self.radioButtonMinuteFrequency)

        self.radioButtonSecondFrequency = QRadioButton(self.groupBoxFrequency)
        self.radioButtonSecondFrequency.setObjectName(u"radioButtonSecondFrequency")

        self.verticalLayout_5.addWidget(self.radioButtonSecondFrequency)


        self.verticalLayout_6.addWidget(self.groupBoxFrequency)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.periodLabel = QLabel(self.groupBoxSettings)
        self.periodLabel.setObjectName(u"periodLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.periodLabel)

        self.periodSpinBox = QSpinBox(self.groupBoxSettings)
        self.periodSpinBox.setObjectName(u"periodSpinBox")
        self.periodSpinBox.setMaximum(1000000000)
        self.periodSpinBox.setValue(60)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.periodSpinBox)


        self.verticalLayout_6.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.groupBoxSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(DecompositionWidget)

        QMetaObject.connectSlotsByName(DecompositionWidget)
    # setupUi

    def retranslateUi(self, DecompositionWidget):
        DecompositionWidget.setWindowTitle(QCoreApplication.translate("DecompositionWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("DecompositionWidget", u"Analyze", None))
        self.groupBoxSettings.setTitle(QCoreApplication.translate("DecompositionWidget", u"Settings", None))
        self.groupBoxMethod.setTitle(QCoreApplication.translate("DecompositionWidget", u"Method", None))
#if QT_CONFIG(tooltip)
        self.radioButtonMethodNaive.setToolTip(QCoreApplication.translate("DecompositionWidget", u"Seasonal decomposition using moving averages", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonMethodNaive.setText(QCoreApplication.translate("DecompositionWidget", u"Naive", None))
#if QT_CONFIG(tooltip)
        self.radioButtonMethodSTL.setToolTip(QCoreApplication.translate("DecompositionWidget", u"Season-Trend decomposition using LOESS", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonMethodSTL.setText(QCoreApplication.translate("DecompositionWidget", u"STL", None))
#if QT_CONFIG(tooltip)
        self.radioButtonMethodMSTL.setToolTip(QCoreApplication.translate("DecompositionWidget", u"Multiple Seasonal-Trend decomposition using LOESS", None))
#endif // QT_CONFIG(tooltip)
        self.radioButtonMethodMSTL.setText(QCoreApplication.translate("DecompositionWidget", u"MSTL", None))
        self.groupBoxModel.setTitle(QCoreApplication.translate("DecompositionWidget", u"Model", None))
        self.radioButtonModelAdditive.setText(QCoreApplication.translate("DecompositionWidget", u"Additive", None))
        self.radioButtonModelMultiplicative.setText(QCoreApplication.translate("DecompositionWidget", u"Multiplicative", None))
        self.groupBoxFrequency.setTitle(QCoreApplication.translate("DecompositionWidget", u"Frequency", None))
        self.radioButtonDayFrequency.setText(QCoreApplication.translate("DecompositionWidget", u"Day", None))
        self.radioButtonHourFrequency.setText(QCoreApplication.translate("DecompositionWidget", u"Hour", None))
        self.radioButtonMinuteFrequency.setText(QCoreApplication.translate("DecompositionWidget", u"Minute", None))
        self.radioButtonSecondFrequency.setText(QCoreApplication.translate("DecompositionWidget", u"Second", None))
        self.periodLabel.setText(QCoreApplication.translate("DecompositionWidget", u"Period", None))
    # retranslateUi

