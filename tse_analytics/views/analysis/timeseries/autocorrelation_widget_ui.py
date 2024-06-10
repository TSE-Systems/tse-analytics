# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'autocorrelation_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QSplitter, QToolButton, QVBoxLayout, QWidget)

from tse_analytics.views.misc.MplCanvas import MplCanvas
import resources_rc

class Ui_AutocorrelationWidget(object):
    def setupUi(self, AutocorrelationWidget):
        if not AutocorrelationWidget.objectName():
            AutocorrelationWidget.setObjectName(u"AutocorrelationWidget")
        AutocorrelationWidget.resize(971, 756)
        self.verticalLayout = QVBoxLayout(AutocorrelationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAnalyse = QToolButton(AutocorrelationWidget)
        self.toolButtonAnalyse.setObjectName(u"toolButtonAnalyse")
        self.toolButtonAnalyse.setEnabled(False)

        self.horizontalLayout.addWidget(self.toolButtonAnalyse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(AutocorrelationWidget)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(AutocorrelationWidget)
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
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.adjustedLabel = QLabel(self.groupBoxSettings)
        self.adjustedLabel.setObjectName(u"adjustedLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.adjustedLabel)

        self.adjustedCheckBox = QCheckBox(self.groupBoxSettings)
        self.adjustedCheckBox.setObjectName(u"adjustedCheckBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.adjustedCheckBox)


        self.verticalLayout_6.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.groupBoxSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(AutocorrelationWidget)

        QMetaObject.connectSlotsByName(AutocorrelationWidget)
    # setupUi

    def retranslateUi(self, AutocorrelationWidget):
        AutocorrelationWidget.setWindowTitle(QCoreApplication.translate("AutocorrelationWidget", u"Form", None))
        self.toolButtonAnalyse.setText(QCoreApplication.translate("AutocorrelationWidget", u"Analyze", None))
        self.groupBoxSettings.setTitle(QCoreApplication.translate("AutocorrelationWidget", u"Settings", None))
        self.adjustedLabel.setText(QCoreApplication.translate("AutocorrelationWidget", u"Adjusted", None))
    # retranslateUi

