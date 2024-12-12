# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'actimot_plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from tse_analytics.modules.phenomaster.actimot.views.actimot_plot_view import ActimotPlotView
from tse_analytics.views.misc.variable_selector import VariableSelector

class Ui_ActimotPlotWidget(object):
    def setupUi(self, ActimotPlotWidget):
        if not ActimotPlotWidget.objectName():
            ActimotPlotWidget.setObjectName(u"ActimotPlotWidget")
        self.verticalLayout = QVBoxLayout(ActimotPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(ActimotPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.variableSelector = VariableSelector(ActimotPlotWidget)
        self.variableSelector.setObjectName(u"variableSelector")

        self.horizontalLayout.addWidget(self.variableSelector)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.plotView = ActimotPlotView(ActimotPlotWidget)
        self.plotView.setObjectName(u"plotView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plotView.sizePolicy().hasHeightForWidth())
        self.plotView.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.plotView)


        self.retranslateUi(ActimotPlotWidget)

        QMetaObject.connectSlotsByName(ActimotPlotWidget)
    # setupUi

    def retranslateUi(self, ActimotPlotWidget):
        self.label.setText(QCoreApplication.translate("ActimotPlotWidget", u"Variable:", None))
        pass
    # retranslateUi

