# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QToolButton,
    QVBoxLayout, QWidget)

from tse_analytics.views.misc.variable_selector import VariableSelector
import resources_rc

class Ui_DataWidget(object):
    def setupUi(self, DataWidget):
        if not DataWidget.objectName():
            DataWidget.setObjectName(u"DataWidget")
        self.verticalLayout = QVBoxLayout(DataWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(DataWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(DataWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.toolButtonDisplayErrors = QToolButton(DataWidget)
        self.toolButtonDisplayErrors.setObjectName(u"toolButtonDisplayErrors")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-sorting-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonDisplayErrors.setIcon(icon)
        self.toolButtonDisplayErrors.setCheckable(True)
        self.toolButtonDisplayErrors.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.toolButtonDisplayErrors)

        self.comboBoxErrorType = QComboBox(DataWidget)
        self.comboBoxErrorType.setObjectName(u"comboBoxErrorType")

        self.horizontalLayout.addWidget(self.comboBoxErrorType)

        self.checkBoxScatterPlot = QCheckBox(DataWidget)
        self.checkBoxScatterPlot.setObjectName(u"checkBoxScatterPlot")

        self.horizontalLayout.addWidget(self.checkBoxScatterPlot)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(DataWidget)

        QMetaObject.connectSlotsByName(DataWidget)
    # setupUi

    def retranslateUi(self, DataWidget):
        self.label.setText(QCoreApplication.translate("DataWidget", u"Variable:", None))
        self.toolButtonDisplayErrors.setText(QCoreApplication.translate("DataWidget", u"Display Errors", None))
        self.checkBoxScatterPlot.setText(QCoreApplication.translate("DataWidget", u"Scatter Plot", None))
        pass
    # retranslateUi

