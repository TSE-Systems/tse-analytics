# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'exclude_time_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDateTimeEdit, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_ExcludeTimeDialog(object):
    def setupUi(self, ExcludeTimeDialog):
        if not ExcludeTimeDialog.objectName():
            ExcludeTimeDialog.setObjectName(u"ExcludeTimeDialog")
        ExcludeTimeDialog.resize(440, 106)
        self.verticalLayout = QVBoxLayout(ExcludeTimeDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxName = QGroupBox(ExcludeTimeDialog)
        self.groupBoxName.setObjectName(u"groupBoxName")
        self.horizontalLayout = QHBoxLayout(self.groupBoxName)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.dateTimeEditStart = QDateTimeEdit(self.groupBoxName)
        self.dateTimeEditStart.setObjectName(u"dateTimeEditStart")

        self.horizontalLayout.addWidget(self.dateTimeEditStart)

        self.dateTimeEditEnd = QDateTimeEdit(self.groupBoxName)
        self.dateTimeEditEnd.setObjectName(u"dateTimeEditEnd")

        self.horizontalLayout.addWidget(self.dateTimeEditEnd)


        self.verticalLayout.addWidget(self.groupBoxName)

        self.buttonBox = QDialogButtonBox(ExcludeTimeDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ExcludeTimeDialog)
        self.buttonBox.accepted.connect(ExcludeTimeDialog.accept)
        self.buttonBox.rejected.connect(ExcludeTimeDialog.reject)

        QMetaObject.connectSlotsByName(ExcludeTimeDialog)
    # setupUi

    def retranslateUi(self, ExcludeTimeDialog):
        ExcludeTimeDialog.setWindowTitle(QCoreApplication.translate("ExcludeTimeDialog", u"Exclude Time", None))
        self.groupBoxName.setTitle(QCoreApplication.translate("ExcludeTimeDialog", u"Select time range to exclude", None))
        self.dateTimeEditStart.setDisplayFormat(QCoreApplication.translate("ExcludeTimeDialog", u"yyyy-MM-dd HH:mm:ss", None))
        self.dateTimeEditEnd.setDisplayFormat(QCoreApplication.translate("ExcludeTimeDialog", u"yyyy-MM-dd HH:mm:ss", None))
    # retranslateUi

