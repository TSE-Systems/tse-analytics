# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_datatable_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)
import resources_rc

class Ui_EditDatatableDialog(object):
    def setupUi(self, EditDatatableDialog):
        if not EditDatatableDialog.objectName():
            EditDatatableDialog.setObjectName(u"EditDatatableDialog")
        EditDatatableDialog.resize(765, 581)
        self.verticalLayout = QVBoxLayout(EditDatatableDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxVariable = QGroupBox(EditDatatableDialog)
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


        self.verticalLayout.addWidget(self.groupBoxVariable)

        self.widgetLayoutH = QWidget(EditDatatableDialog)
        self.widgetLayoutH.setObjectName(u"widgetLayoutH")
        self.horizontalLayout = QHBoxLayout(self.widgetLayoutH)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBoxAnimals = QGroupBox(self.widgetLayoutH)
        self.groupBoxAnimals.setObjectName(u"groupBoxAnimals")
        self.groupBoxAnimals.setCheckable(True)
        self.groupBoxAnimals.setChecked(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxAnimals)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tableWidgetAnimals = QTableWidget(self.groupBoxAnimals)
        self.tableWidgetAnimals.setObjectName(u"tableWidgetAnimals")
        self.tableWidgetAnimals.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidgetAnimals.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.tableWidgetAnimals.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidgetAnimals.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableWidgetAnimals.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableWidgetAnimals.setSortingEnabled(True)
        self.tableWidgetAnimals.verticalHeader().setVisible(False)
        self.tableWidgetAnimals.verticalHeader().setMinimumSectionSize(20)
        self.tableWidgetAnimals.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_2.addWidget(self.tableWidgetAnimals)


        self.horizontalLayout.addWidget(self.groupBoxAnimals)

        self.widgetLayoutV = QWidget(self.widgetLayoutH)
        self.widgetLayoutV.setObjectName(u"widgetLayoutV")
        self.widgetLayoutV.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.widgetLayoutV)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxResampling = QGroupBox(self.widgetLayoutV)
        self.groupBoxResampling.setObjectName(u"groupBoxResampling")
        self.groupBoxResampling.setCheckable(True)
        self.groupBoxResampling.setChecked(False)
        self.verticalLayout_5 = QVBoxLayout(self.groupBoxResampling)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.widgetIntervals = QWidget(self.groupBoxResampling)
        self.widgetIntervals.setObjectName(u"widgetIntervals")
        self.horizontalLayout_3 = QHBoxLayout(self.widgetIntervals)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.deltaSpinBox = QSpinBox(self.widgetIntervals)
        self.deltaSpinBox.setObjectName(u"deltaSpinBox")
        self.deltaSpinBox.setMinimum(1)
        self.deltaSpinBox.setMaximum(1000)

        self.horizontalLayout_3.addWidget(self.deltaSpinBox)

        self.unitComboBox = QComboBox(self.widgetIntervals)
        self.unitComboBox.setObjectName(u"unitComboBox")

        self.horizontalLayout_3.addWidget(self.unitComboBox)


        self.verticalLayout_5.addWidget(self.widgetIntervals)


        self.verticalLayout_3.addWidget(self.groupBoxResampling)

        self.verticalSpacer = QSpacerItem(20, 351, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.widgetLayoutV)


        self.verticalLayout.addWidget(self.widgetLayoutH)

        self.buttonBox = QDialogButtonBox(EditDatatableDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(EditDatatableDialog)
        self.buttonBox.accepted.connect(EditDatatableDialog.accept)
        self.buttonBox.rejected.connect(EditDatatableDialog.reject)

        QMetaObject.connectSlotsByName(EditDatatableDialog)
    # setupUi

    def retranslateUi(self, EditDatatableDialog):
        EditDatatableDialog.setWindowTitle(QCoreApplication.translate("EditDatatableDialog", u"Edit Datatable", None))
        self.nameLabel.setText(QCoreApplication.translate("EditDatatableDialog", u"Name:", None))
        self.descriptionLabel.setText(QCoreApplication.translate("EditDatatableDialog", u"Description:", None))
        self.groupBoxAnimals.setTitle(QCoreApplication.translate("EditDatatableDialog", u"Exclude Animals", None))
        self.groupBoxResampling.setTitle(QCoreApplication.translate("EditDatatableDialog", u"Resampling", None))
    # retranslateUi

