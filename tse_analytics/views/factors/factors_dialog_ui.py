# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'factors_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_FactorsDialog(object):
    def setupUi(self, FactorsDialog):
        if not FactorsDialog.objectName():
            FactorsDialog.setObjectName(u"FactorsDialog")
        FactorsDialog.resize(704, 513)
        self.verticalLayout_8 = QVBoxLayout(FactorsDialog)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxFactors = QGroupBox(FactorsDialog)
        self.groupBoxFactors.setObjectName(u"groupBoxFactors")
        self.verticalLayout = QVBoxLayout(self.groupBoxFactors)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listWidgetFactors = QListWidget(self.groupBoxFactors)
        self.listWidgetFactors.setObjectName(u"listWidgetFactors")

        self.verticalLayout.addWidget(self.listWidgetFactors)

        self.pushButtonAddFactor = QPushButton(self.groupBoxFactors)
        self.pushButtonAddFactor.setObjectName(u"pushButtonAddFactor")

        self.verticalLayout.addWidget(self.pushButtonAddFactor)

        self.pushButtonDeleteFactor = QPushButton(self.groupBoxFactors)
        self.pushButtonDeleteFactor.setObjectName(u"pushButtonDeleteFactor")
        self.pushButtonDeleteFactor.setEnabled(False)

        self.verticalLayout.addWidget(self.pushButtonDeleteFactor)


        self.horizontalLayout.addWidget(self.groupBoxFactors)

        self.groupBoxLevels = QGroupBox(FactorsDialog)
        self.groupBoxLevels.setObjectName(u"groupBoxLevels")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxLevels)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listWidgetLevels = QListWidget(self.groupBoxLevels)
        self.listWidgetLevels.setObjectName(u"listWidgetLevels")

        self.verticalLayout_3.addWidget(self.listWidgetLevels)

        self.pushButtonAddLevel = QPushButton(self.groupBoxLevels)
        self.pushButtonAddLevel.setObjectName(u"pushButtonAddLevel")
        self.pushButtonAddLevel.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonAddLevel)

        self.pushButtonDeleteLevel = QPushButton(self.groupBoxLevels)
        self.pushButtonDeleteLevel.setObjectName(u"pushButtonDeleteLevel")
        self.pushButtonDeleteLevel.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonDeleteLevel)

        self.pushButtonExtractLevels = QPushButton(self.groupBoxLevels)
        self.pushButtonExtractLevels.setObjectName(u"pushButtonExtractLevels")
        self.pushButtonExtractLevels.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonExtractLevels)

        self.comboBoxFields = QComboBox(self.groupBoxLevels)
        self.comboBoxFields.setObjectName(u"comboBoxFields")
        self.comboBoxFields.setEnabled(False)

        self.verticalLayout_3.addWidget(self.comboBoxFields)


        self.horizontalLayout.addWidget(self.groupBoxLevels)

        self.groupBoxAnimals = QGroupBox(FactorsDialog)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.listWidgetAnimals = QListWidget(self.groupBoxAnimals)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")

        self.verticalLayout_4.addWidget(self.listWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)


        self.verticalLayout_8.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(FactorsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_8.addWidget(self.buttonBox)


        self.retranslateUi(FactorsDialog)
        self.buttonBox.accepted.connect(FactorsDialog.accept)
        self.buttonBox.rejected.connect(FactorsDialog.reject)

        QMetaObject.connectSlotsByName(FactorsDialog)
    # setupUi

    def retranslateUi(self, FactorsDialog):
        FactorsDialog.setWindowTitle(QCoreApplication.translate("FactorsDialog", u"Factors", None))
        self.groupBoxFactors.setTitle(QCoreApplication.translate("FactorsDialog", u"Factors", None))
        self.pushButtonAddFactor.setText(QCoreApplication.translate("FactorsDialog", u"Add Factor", None))
        self.pushButtonDeleteFactor.setText(QCoreApplication.translate("FactorsDialog", u"Delete Factor", None))
        self.groupBoxLevels.setTitle(QCoreApplication.translate("FactorsDialog", u"Levels", None))
        self.pushButtonAddLevel.setText(QCoreApplication.translate("FactorsDialog", u"Add Level", None))
        self.pushButtonDeleteLevel.setText(QCoreApplication.translate("FactorsDialog", u"Delete Level", None))
        self.pushButtonExtractLevels.setText(QCoreApplication.translate("FactorsDialog", u"Extract levels from...", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("FactorsDialog", u"Animals", None))
    # retranslateUi

