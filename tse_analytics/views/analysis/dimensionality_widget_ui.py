# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dimensionality_widget.ui'
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QGroupBox, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QSplitter, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.factor_selector import FactorSelector
import resources_rc

class Ui_DimensionalityWidget(object):
    def setupUi(self, DimensionalityWidget):
        if not DimensionalityWidget.objectName():
            DimensionalityWidget.setObjectName(u"DimensionalityWidget")
        DimensionalityWidget.resize(162, 435)
        self.verticalLayout = QVBoxLayout(DimensionalityWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(DimensionalityWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.webView = QWebEngineView(self.splitter)
        self.webView.setObjectName(u"webView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)
        self.splitter.addWidget(self.webView)
        self.widgetSettings = QWidget(self.splitter)
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayout_2 = QVBoxLayout(self.widgetSettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxAnalysis = QGroupBox(self.widgetSettings)
        self.groupBoxAnalysis.setObjectName(u"groupBoxAnalysis")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxAnalysis)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButtonMatrixPlot = QRadioButton(self.groupBoxAnalysis)
        self.radioButtonMatrixPlot.setObjectName(u"radioButtonMatrixPlot")
        self.radioButtonMatrixPlot.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButtonMatrixPlot)

        self.radioButtonPCA = QRadioButton(self.groupBoxAnalysis)
        self.radioButtonPCA.setObjectName(u"radioButtonPCA")

        self.verticalLayout_3.addWidget(self.radioButtonPCA)

        self.radioButtonTSNE = QRadioButton(self.groupBoxAnalysis)
        self.radioButtonTSNE.setObjectName(u"radioButtonTSNE")

        self.verticalLayout_3.addWidget(self.radioButtonTSNE)


        self.verticalLayout_2.addWidget(self.groupBoxAnalysis)

        self.groupBoxDimensions = QGroupBox(self.widgetSettings)
        self.groupBoxDimensions.setObjectName(u"groupBoxDimensions")
        self.groupBoxDimensions.setEnabled(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxDimensions)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.radioButton2D = QRadioButton(self.groupBoxDimensions)
        self.radioButton2D.setObjectName(u"radioButton2D")
        self.radioButton2D.setChecked(True)

        self.verticalLayout_5.addWidget(self.radioButton2D)

        self.radioButton3D = QRadioButton(self.groupBoxDimensions)
        self.radioButton3D.setObjectName(u"radioButton3D")

        self.verticalLayout_5.addWidget(self.radioButton3D)


        self.verticalLayout_2.addWidget(self.groupBoxDimensions)

        self.groupBoxFactor = QGroupBox(self.widgetSettings)
        self.groupBoxFactor.setObjectName(u"groupBoxFactor")
        self.groupBoxFactor.setCheckable(True)
        self.groupBoxFactor.setChecked(False)
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxFactor)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.factorSelector = FactorSelector(self.groupBoxFactor)
        self.factorSelector.setObjectName(u"factorSelector")

        self.verticalLayout_6.addWidget(self.factorSelector)


        self.verticalLayout_2.addWidget(self.groupBoxFactor)

        self.pushButtonUpdate = QPushButton(self.widgetSettings)
        self.pushButtonUpdate.setObjectName(u"pushButtonUpdate")
        self.pushButtonUpdate.setEnabled(False)

        self.verticalLayout_2.addWidget(self.pushButtonUpdate)

        self.pushButtonHelp = QPushButton(self.widgetSettings)
        self.pushButtonHelp.setObjectName(u"pushButtonHelp")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButtonHelp.setIcon(icon)

        self.verticalLayout_2.addWidget(self.pushButtonHelp)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.widgetSettings)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(DimensionalityWidget)

        QMetaObject.connectSlotsByName(DimensionalityWidget)
    # setupUi

    def retranslateUi(self, DimensionalityWidget):
        self.groupBoxAnalysis.setTitle(QCoreApplication.translate("DimensionalityWidget", u"Analysis", None))
        self.radioButtonMatrixPlot.setText(QCoreApplication.translate("DimensionalityWidget", u"Matrix Plot", None))
        self.radioButtonPCA.setText(QCoreApplication.translate("DimensionalityWidget", u"PCA", None))
        self.radioButtonTSNE.setText(QCoreApplication.translate("DimensionalityWidget", u"t-SNE", None))
        self.groupBoxDimensions.setTitle(QCoreApplication.translate("DimensionalityWidget", u"Dimensions", None))
        self.radioButton2D.setText(QCoreApplication.translate("DimensionalityWidget", u"2D", None))
        self.radioButton3D.setText(QCoreApplication.translate("DimensionalityWidget", u"3D", None))
        self.groupBoxFactor.setTitle(QCoreApplication.translate("DimensionalityWidget", u"Split by factor", None))
        self.pushButtonUpdate.setText(QCoreApplication.translate("DimensionalityWidget", u"Update", None))
        self.pushButtonHelp.setText(QCoreApplication.translate("DimensionalityWidget", u"Help", None))
        pass
    # retranslateUi

