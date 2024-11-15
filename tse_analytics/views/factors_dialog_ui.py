# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'factors_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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

        self.groupBoxGroups = QGroupBox(FactorsDialog)
        self.groupBoxGroups.setObjectName(u"groupBoxGroups")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxGroups)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listWidgetGroups = QListWidget(self.groupBoxGroups)
        self.listWidgetGroups.setObjectName(u"listWidgetGroups")

        self.verticalLayout_3.addWidget(self.listWidgetGroups)

        self.pushButtonAddGroup = QPushButton(self.groupBoxGroups)
        self.pushButtonAddGroup.setObjectName(u"pushButtonAddGroup")
        self.pushButtonAddGroup.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonAddGroup)

        self.pushButtonDeleteGroup = QPushButton(self.groupBoxGroups)
        self.pushButtonDeleteGroup.setObjectName(u"pushButtonDeleteGroup")
        self.pushButtonDeleteGroup.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonDeleteGroup)

        self.pushButtonExtractGroups = QPushButton(self.groupBoxGroups)
        self.pushButtonExtractGroups.setObjectName(u"pushButtonExtractGroups")
        self.pushButtonExtractGroups.setEnabled(False)

        self.verticalLayout_3.addWidget(self.pushButtonExtractGroups)

        self.comboBoxFields = QComboBox(self.groupBoxGroups)
        self.comboBoxFields.setObjectName(u"comboBoxFields")
        self.comboBoxFields.setEnabled(False)

        self.verticalLayout_3.addWidget(self.comboBoxFields)


        self.horizontalLayout.addWidget(self.groupBoxGroups)

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
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

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
        self.groupBoxGroups.setTitle(QCoreApplication.translate("FactorsDialog", u"Groups", None))
        self.pushButtonAddGroup.setText(QCoreApplication.translate("FactorsDialog", u"Add Group", None))
        self.pushButtonDeleteGroup.setText(QCoreApplication.translate("FactorsDialog", u"Delete Group", None))
        self.pushButtonExtractGroups.setText(QCoreApplication.translate("FactorsDialog", u"Extract from...", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("FactorsDialog", u"Animals", None))
    # retranslateUi

