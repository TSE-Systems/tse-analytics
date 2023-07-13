# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'time_intervals_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGroupBox,
    QLabel, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_TimeIntervalsSettingsWidget(object):
    def setupUi(self, TimeIntervalsSettingsWidget):
        if not TimeIntervalsSettingsWidget.objectName():
            TimeIntervalsSettingsWidget.setObjectName(u"TimeIntervalsSettingsWidget")
        TimeIntervalsSettingsWidget.resize(546, 585)
        self.verticalLayout = QVBoxLayout(TimeIntervalsSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxIntervals = QGroupBox(TimeIntervalsSettingsWidget)
        self.groupBoxIntervals.setObjectName(u"groupBoxIntervals")
        self.formLayout = QFormLayout(self.groupBoxIntervals)
        self.formLayout.setObjectName(u"formLayout")
        self.unitLabel = QLabel(self.groupBoxIntervals)
        self.unitLabel.setObjectName(u"unitLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.unitLabel)

        self.unitComboBox = QComboBox(self.groupBoxIntervals)
        self.unitComboBox.setObjectName(u"unitComboBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.unitComboBox)

        self.deltaLabel = QLabel(self.groupBoxIntervals)
        self.deltaLabel.setObjectName(u"deltaLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.deltaLabel)

        self.deltaSpinBox = QSpinBox(self.groupBoxIntervals)
        self.deltaSpinBox.setObjectName(u"deltaSpinBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.deltaSpinBox)


        self.verticalLayout.addWidget(self.groupBoxIntervals)


        self.retranslateUi(TimeIntervalsSettingsWidget)

        QMetaObject.connectSlotsByName(TimeIntervalsSettingsWidget)
    # setupUi

    def retranslateUi(self, TimeIntervalsSettingsWidget):
        TimeIntervalsSettingsWidget.setWindowTitle(QCoreApplication.translate("TimeIntervalsSettingsWidget", u"Form", None))
        self.groupBoxIntervals.setTitle(QCoreApplication.translate("TimeIntervalsSettingsWidget", u"Time Intervals", None))
        self.unitLabel.setText(QCoreApplication.translate("TimeIntervalsSettingsWidget", u"Unit", None))
        self.deltaLabel.setText(QCoreApplication.translate("TimeIntervalsSettingsWidget", u"Delta", None))
    # retranslateUi

