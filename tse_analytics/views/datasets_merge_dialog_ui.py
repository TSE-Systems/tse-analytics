# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'datasets_merge_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
    QDialogButtonBox, QGroupBox, QLineEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_DatasetsMergeDialog(object):
    def setupUi(self, DatasetsMergeDialog):
        if not DatasetsMergeDialog.objectName():
            DatasetsMergeDialog.setObjectName(u"DatasetsMergeDialog")
        DatasetsMergeDialog.resize(440, 132)
        self.verticalLayout = QVBoxLayout(DatasetsMergeDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxName = QGroupBox(DatasetsMergeDialog)
        self.groupBoxName.setObjectName(u"groupBoxName")
        self._3 = QVBoxLayout(self.groupBoxName)
        self._3.setObjectName(u"_3")
        self.lineEditName = QLineEdit(self.groupBoxName)
        self.lineEditName.setObjectName(u"lineEditName")

        self._3.addWidget(self.lineEditName)


        self.verticalLayout.addWidget(self.groupBoxName)

        self.checkBoxSingleRun = QCheckBox(DatasetsMergeDialog)
        self.checkBoxSingleRun.setObjectName(u"checkBoxSingleRun")

        self.verticalLayout.addWidget(self.checkBoxSingleRun)

        self.buttonBox = QDialogButtonBox(DatasetsMergeDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DatasetsMergeDialog)
        self.buttonBox.accepted.connect(DatasetsMergeDialog.accept)
        self.buttonBox.rejected.connect(DatasetsMergeDialog.reject)

        QMetaObject.connectSlotsByName(DatasetsMergeDialog)
    # setupUi

    def retranslateUi(self, DatasetsMergeDialog):
        DatasetsMergeDialog.setWindowTitle(QCoreApplication.translate("DatasetsMergeDialog", u"Merge Datasets", None))
        self.groupBoxName.setTitle(QCoreApplication.translate("DatasetsMergeDialog", u"Merged dataset name", None))
        self.checkBoxSingleRun.setText(QCoreApplication.translate("DatasetsMergeDialog", u"Merge as a single run", None))
    # retranslateUi

