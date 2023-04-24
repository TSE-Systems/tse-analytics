# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'datasets_merge_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_DatasetsMergeDialog(object):
    def setupUi(self, DatasetsMergeDialog):
        if not DatasetsMergeDialog.objectName():
            DatasetsMergeDialog.setObjectName("DatasetsMergeDialog")
        DatasetsMergeDialog.resize(440, 132)
        self._4 = QVBoxLayout(DatasetsMergeDialog)
        self._4.setObjectName("_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBoxName = QGroupBox(DatasetsMergeDialog)
        self.groupBoxName.setObjectName("groupBoxName")
        self._3 = QVBoxLayout(self.groupBoxName)
        self._3.setObjectName("_3")
        self.lineEditName = QLineEdit(self.groupBoxName)
        self.lineEditName.setObjectName("lineEditName")

        self._3.addWidget(self.lineEditName)

        self.horizontalLayout.addWidget(self.groupBoxName, 0, Qt.AlignTop)

        self.groupBoxMergeMode = QGroupBox(DatasetsMergeDialog)
        self.groupBoxMergeMode.setObjectName("groupBoxMergeMode")
        self._2 = QVBoxLayout(self.groupBoxMergeMode)
        self._2.setObjectName("_2")
        self.radioButtonConcatenation = QRadioButton(self.groupBoxMergeMode)
        self.radioButtonConcatenation.setObjectName("radioButtonConcatenation")
        self.radioButtonConcatenation.setChecked(True)

        self._2.addWidget(self.radioButtonConcatenation)

        self.radioButtonOverlap = QRadioButton(self.groupBoxMergeMode)
        self.radioButtonOverlap.setObjectName("radioButtonOverlap")

        self._2.addWidget(self.radioButtonOverlap)

        self.horizontalLayout.addWidget(self.groupBoxMergeMode, 0, Qt.AlignTop)

        self._4.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(DatasetsMergeDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self._4.addWidget(self.buttonBox)

        self.retranslateUi(DatasetsMergeDialog)
        self.buttonBox.accepted.connect(DatasetsMergeDialog.accept)
        self.buttonBox.rejected.connect(DatasetsMergeDialog.reject)

        QMetaObject.connectSlotsByName(DatasetsMergeDialog)

    # setupUi

    def retranslateUi(self, DatasetsMergeDialog):
        DatasetsMergeDialog.setWindowTitle(QCoreApplication.translate("DatasetsMergeDialog", "Merge Datasets", None))
        self.groupBoxName.setTitle(QCoreApplication.translate("DatasetsMergeDialog", "Merged dataset name", None))
        self.groupBoxMergeMode.setTitle(QCoreApplication.translate("DatasetsMergeDialog", "Merge mode", None))
        self.radioButtonConcatenation.setText(QCoreApplication.translate("DatasetsMergeDialog", "Concatenation", None))
        self.radioButtonOverlap.setText(QCoreApplication.translate("DatasetsMergeDialog", "Overlap", None))

    # retranslateUi
