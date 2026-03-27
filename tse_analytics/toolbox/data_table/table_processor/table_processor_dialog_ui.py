# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'table_processor_dialog.ui'
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
    QDialogButtonBox, QFormLayout, QGroupBox, QLabel,
    QLineEdit, QRadioButton, QSizePolicy, QVBoxLayout,
    QWidget)

from tse_analytics.views.misc.variable_selector import VariableSelector

class Ui_TableProcessorDialog(object):
    def setupUi(self, TableProcessorDialog):
        if not TableProcessorDialog.objectName():
            TableProcessorDialog.setObjectName(u"TableProcessorDialog")
        TableProcessorDialog.resize(406, 579)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TableProcessorDialog.sizePolicy().hasHeightForWidth())
        TableProcessorDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(TableProcessorDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxVariable = QGroupBox(TableProcessorDialog)
        self.groupBoxVariable.setObjectName(u"groupBoxVariable")
        self.formLayout = QFormLayout(self.groupBoxVariable)
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(self.groupBoxVariable)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(self.groupBoxVariable)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.descriptionLabel = QLabel(self.groupBoxVariable)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.descriptionLineEdit = QLineEdit(self.groupBoxVariable)
        self.descriptionLineEdit.setObjectName(u"descriptionLineEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.descriptionLineEdit)

        self.unitLabel = QLabel(self.groupBoxVariable)
        self.unitLabel.setObjectName(u"unitLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.unitLabel)

        self.unitLineEdit = QLineEdit(self.groupBoxVariable)
        self.unitLineEdit.setObjectName(u"unitLineEdit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.unitLineEdit)

        self.aggregationLabel = QLabel(self.groupBoxVariable)
        self.aggregationLabel.setObjectName(u"aggregationLabel")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.aggregationLabel)

        self.aggregationComboBox = QComboBox(self.groupBoxVariable)
        self.aggregationComboBox.setObjectName(u"aggregationComboBox")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.aggregationComboBox)


        self.verticalLayout.addWidget(self.groupBoxVariable)

        self.groupBoxOrigin = QGroupBox(TableProcessorDialog)
        self.groupBoxOrigin.setObjectName(u"groupBoxOrigin")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxOrigin)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButtonOriginAnimalProperty = QRadioButton(self.groupBoxOrigin)
        self.radioButtonOriginAnimalProperty.setObjectName(u"radioButtonOriginAnimalProperty")
        self.radioButtonOriginAnimalProperty.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButtonOriginAnimalProperty)

        self.radioButtonOriginCumulative = QRadioButton(self.groupBoxOrigin)
        self.radioButtonOriginCumulative.setObjectName(u"radioButtonOriginCumulative")

        self.verticalLayout_3.addWidget(self.radioButtonOriginCumulative)

        self.radioButtonOriginDifferential = QRadioButton(self.groupBoxOrigin)
        self.radioButtonOriginDifferential.setObjectName(u"radioButtonOriginDifferential")

        self.verticalLayout_3.addWidget(self.radioButtonOriginDifferential)

        self.radioButtonOriginExpression = QRadioButton(self.groupBoxOrigin)
        self.radioButtonOriginExpression.setObjectName(u"radioButtonOriginExpression")

        self.verticalLayout_3.addWidget(self.radioButtonOriginExpression)


        self.verticalLayout.addWidget(self.groupBoxOrigin)

        self.groupBoxAnimalProperty = QGroupBox(TableProcessorDialog)
        self.groupBoxAnimalProperty.setObjectName(u"groupBoxAnimalProperty")
        self.verticalLayout_4 = QVBoxLayout(self.groupBoxAnimalProperty)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.comboBoxAnimalProperty = QComboBox(self.groupBoxAnimalProperty)
        self.comboBoxAnimalProperty.setObjectName(u"comboBoxAnimalProperty")

        self.verticalLayout_4.addWidget(self.comboBoxAnimalProperty)


        self.verticalLayout.addWidget(self.groupBoxAnimalProperty)

        self.groupBoxOriginVariable = QGroupBox(TableProcessorDialog)
        self.groupBoxOriginVariable.setObjectName(u"groupBoxOriginVariable")
        self.groupBoxOriginVariable.setEnabled(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxOriginVariable)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.variableSelector = VariableSelector(self.groupBoxOriginVariable)
        self.variableSelector.setObjectName(u"variableSelector")

        self.verticalLayout_5.addWidget(self.variableSelector)


        self.verticalLayout.addWidget(self.groupBoxOriginVariable)

        self.groupBoxExpression = QGroupBox(TableProcessorDialog)
        self.groupBoxExpression.setObjectName(u"groupBoxExpression")
        self.groupBoxExpression.setEnabled(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxExpression)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lineEditExpression = QLineEdit(self.groupBoxExpression)
        self.lineEditExpression.setObjectName(u"lineEditExpression")

        self.verticalLayout_2.addWidget(self.lineEditExpression)


        self.verticalLayout.addWidget(self.groupBoxExpression)

        self.buttonBox = QDialogButtonBox(TableProcessorDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(TableProcessorDialog)
        self.buttonBox.accepted.connect(TableProcessorDialog.accept)
        self.buttonBox.rejected.connect(TableProcessorDialog.reject)

        QMetaObject.connectSlotsByName(TableProcessorDialog)
    # setupUi

    def retranslateUi(self, TableProcessorDialog):
        TableProcessorDialog.setWindowTitle(QCoreApplication.translate("TableProcessorDialog", u"Add Derived Table", None))
        self.groupBoxVariable.setTitle(QCoreApplication.translate("TableProcessorDialog", u"New Variable", None))
        self.nameLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Name:", None))
        self.descriptionLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Description:", None))
        self.unitLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Unit:", None))
        self.aggregationLabel.setText(QCoreApplication.translate("TableProcessorDialog", u"Aggregation:", None))
        self.groupBoxOrigin.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Origin", None))
        self.radioButtonOriginAnimalProperty.setText(QCoreApplication.translate("TableProcessorDialog", u"Animal property", None))
        self.radioButtonOriginCumulative.setText(QCoreApplication.translate("TableProcessorDialog", u"Cumulative variable", None))
        self.radioButtonOriginDifferential.setText(QCoreApplication.translate("TableProcessorDialog", u"Differential variable", None))
        self.radioButtonOriginExpression.setText(QCoreApplication.translate("TableProcessorDialog", u"Expression", None))
        self.groupBoxAnimalProperty.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Animal Property", None))
        self.groupBoxOriginVariable.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Origin Variable", None))
        self.groupBoxExpression.setTitle(QCoreApplication.translate("TableProcessorDialog", u"Expression", None))
    # retranslateUi

