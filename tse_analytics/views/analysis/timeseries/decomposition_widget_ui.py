# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'decomposition_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QSpinBox, QSplitter, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
import resources_rc

class Ui_DecompositionWidget(object):
    def setupUi(self, DecompositionWidget):
        if not DecompositionWidget.objectName():
            DecompositionWidget.setObjectName(u"DecompositionWidget")
        self.verticalLayout = QVBoxLayout(DecompositionWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
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
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_6 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBoxMethod = QGroupBox(self.widgetSettings)
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

        self.groupBoxModel = QGroupBox(self.widgetSettings)
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

        self.groupBoxFrequency = QGroupBox(self.widgetSettings)
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
        self.periodLabel = QLabel(self.widgetSettings)
        self.periodLabel.setObjectName(u"periodLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.periodLabel)

        self.periodSpinBox = QSpinBox(self.widgetSettings)
        self.periodSpinBox.setObjectName(u"periodSpinBox")
        self.periodSpinBox.setMaximum(1000000000)
        self.periodSpinBox.setValue(60)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.periodSpinBox)


        self.verticalLayout_6.addLayout(self.formLayout)

        self.pushButtonUpdate = QPushButton(self.widgetSettings)
        self.pushButtonUpdate.setObjectName(u"pushButtonUpdate")
        self.pushButtonUpdate.setEnabled(False)

        self.verticalLayout_6.addWidget(self.pushButtonUpdate)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.pushButtonAddReport = QPushButton(self.widgetSettings)
        self.pushButtonAddReport.setObjectName(u"pushButtonAddReport")
        self.pushButtonAddReport.setEnabled(False)

        self.verticalLayout_6.addWidget(self.pushButtonAddReport)

        self.pushButtonHelp = QPushButton(self.widgetSettings)
        self.pushButtonHelp.setObjectName(u"pushButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonHelp.setIcon(icon)

        self.verticalLayout_6.addWidget(self.pushButtonHelp)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(DecompositionWidget)

        QMetaObject.connectSlotsByName(DecompositionWidget)
    # setupUi

    def retranslateUi(self, DecompositionWidget):
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
        self.pushButtonUpdate.setText(QCoreApplication.translate("DecompositionWidget", u"Update", None))
        self.pushButtonAddReport.setText(QCoreApplication.translate("DecompositionWidget", u"Add to Report", None))
        self.pushButtonHelp.setText(QCoreApplication.translate("DecompositionWidget", u"Help", None))
        pass
    # retranslateUi

