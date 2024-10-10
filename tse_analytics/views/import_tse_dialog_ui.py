# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'import_tse_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_ImportTseDialog(object):
    def setupUi(self, ImportTseDialog):
        if not ImportTseDialog.objectName():
            ImportTseDialog.setObjectName(u"ImportTseDialog")
        self.verticalLayout = QVBoxLayout(ImportTseDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBoxImportSettings = QGroupBox(ImportTseDialog)
        self.groupBoxImportSettings.setObjectName(u"groupBoxImportSettings")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxImportSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.checkBoxCalo = QCheckBox(self.groupBoxImportSettings)
        self.checkBoxCalo.setObjectName(u"checkBoxCalo")

        self.verticalLayout_3.addWidget(self.checkBoxCalo)

        self.checkBoxMeal = QCheckBox(self.groupBoxImportSettings)
        self.checkBoxMeal.setObjectName(u"checkBoxMeal")

        self.verticalLayout_3.addWidget(self.checkBoxMeal)

        self.checkBoxActiMot = QCheckBox(self.groupBoxImportSettings)
        self.checkBoxActiMot.setObjectName(u"checkBoxActiMot")

        self.verticalLayout_3.addWidget(self.checkBoxActiMot)


        self.horizontalLayout.addWidget(self.groupBoxImportSettings)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(ImportTseDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ImportTseDialog)
        self.buttonBox.accepted.connect(ImportTseDialog.accept)
        self.buttonBox.rejected.connect(ImportTseDialog.reject)

        QMetaObject.connectSlotsByName(ImportTseDialog)
    # setupUi

    def retranslateUi(self, ImportTseDialog):
        ImportTseDialog.setWindowTitle(QCoreApplication.translate("ImportTseDialog", u"Import Dataset", None))
        self.groupBoxImportSettings.setTitle(QCoreApplication.translate("ImportTseDialog", u"Import", None))
        self.checkBoxCalo.setText(QCoreApplication.translate("ImportTseDialog", u"Calo details data", None))
        self.checkBoxMeal.setText(QCoreApplication.translate("ImportTseDialog", u"Meal details data", None))
        self.checkBoxActiMot.setText(QCoreApplication.translate("ImportTseDialog", u"ActiMot raw data", None))
    # retranslateUi

