# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'prophet_forecasting_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QSplitter,
    QToolButton, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
import resources_rc

class Ui_ProphetForecastingWidget(object):
    def setupUi(self, ProphetForecastingWidget):
        if not ProphetForecastingWidget.objectName():
            ProphetForecastingWidget.setObjectName(u"ProphetForecastingWidget")
        ProphetForecastingWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(ProphetForecastingWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(ProphetForecastingWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(ProphetForecastingWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(ProphetForecastingWidget)
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
        self.changepointPriorScaleLabel = QLabel(self.groupBoxSettings)
        self.changepointPriorScaleLabel.setObjectName(u"changepointPriorScaleLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.changepointPriorScaleLabel)

        self.changepointPriorScaleDoubleSpinBox = QDoubleSpinBox(self.groupBoxSettings)
        self.changepointPriorScaleDoubleSpinBox.setObjectName(u"changepointPriorScaleDoubleSpinBox")
        self.changepointPriorScaleDoubleSpinBox.setValue(0.050000000000000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.changepointPriorScaleDoubleSpinBox)

        self.periodsLabel = QLabel(self.groupBoxSettings)
        self.periodsLabel.setObjectName(u"periodsLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.periodsLabel)

        self.periodsSpinBox = QSpinBox(self.groupBoxSettings)
        self.periodsSpinBox.setObjectName(u"periodsSpinBox")
        self.periodsSpinBox.setMaximum(1000000000)
        self.periodsSpinBox.setValue(60)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.periodsSpinBox)

        self.showTrendLabel = QLabel(self.groupBoxSettings)
        self.showTrendLabel.setObjectName(u"showTrendLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.showTrendLabel)

        self.showTrendCheckBox = QCheckBox(self.groupBoxSettings)
        self.showTrendCheckBox.setObjectName(u"showTrendCheckBox")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.showTrendCheckBox)

        self.showHistoryLabel = QLabel(self.groupBoxSettings)
        self.showHistoryLabel.setObjectName(u"showHistoryLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.showHistoryLabel)

        self.showHistoryCheckBox = QCheckBox(self.groupBoxSettings)
        self.showHistoryCheckBox.setObjectName(u"showHistoryCheckBox")
        self.showHistoryCheckBox.setChecked(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.showHistoryCheckBox)


        self.verticalLayout_6.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.groupBoxSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(ProphetForecastingWidget)

        QMetaObject.connectSlotsByName(ProphetForecastingWidget)
    # setupUi

    def retranslateUi(self, ProphetForecastingWidget):
        ProphetForecastingWidget.setWindowTitle(QCoreApplication.translate("ProphetForecastingWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Analyze", None))
        self.groupBoxSettings.setTitle(QCoreApplication.translate("ProphetForecastingWidget", u"Settings", None))
        self.groupBoxFrequency.setTitle(QCoreApplication.translate("ProphetForecastingWidget", u"Frequency", None))
        self.radioButtonDayFrequency.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Day", None))
        self.radioButtonHourFrequency.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Hour", None))
        self.radioButtonMinuteFrequency.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Minute", None))
        self.radioButtonSecondFrequency.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Second", None))
        self.changepointPriorScaleLabel.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Changepoint Prior Scale", None))
        self.periodsLabel.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Periods", None))
        self.showTrendLabel.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Show Trend", None))
        self.showHistoryLabel.setText(QCoreApplication.translate("ProphetForecastingWidget", u"Show History", None))
    # retranslateUi
