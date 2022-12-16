# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'groups_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QWidget)

class Ui_GroupsDialog(object):
    def setupUi(self, GroupsDialog):
        if not GroupsDialog.objectName():
            GroupsDialog.setObjectName(u"GroupsDialog")
        GroupsDialog.resize(561, 525)
        self.buttonBox = QDialogButtonBox(GroupsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(360, 480, 191, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.horizontalLayoutWidget = QWidget(GroupsDialog)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 10, 541, 451))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.listWidgetGroups = QListWidget(self.horizontalLayoutWidget)
        self.listWidgetGroups.setObjectName(u"listWidgetGroups")

        self.horizontalLayout.addWidget(self.listWidgetGroups)

        self.listWidgetAnimals = QListWidget(self.horizontalLayoutWidget)
        self.listWidgetAnimals.setObjectName(u"listWidgetAnimals")

        self.horizontalLayout.addWidget(self.listWidgetAnimals)

        self.pushButtonAddGroup = QPushButton(GroupsDialog)
        self.pushButtonAddGroup.setObjectName(u"pushButtonAddGroup")
        self.pushButtonAddGroup.setGeometry(QRect(20, 480, 80, 24))
        self.pushButtonDeleteGroup = QPushButton(GroupsDialog)
        self.pushButtonDeleteGroup.setObjectName(u"pushButtonDeleteGroup")
        self.pushButtonDeleteGroup.setGeometry(QRect(110, 480, 80, 24))

        self.retranslateUi(GroupsDialog)
        self.buttonBox.accepted.connect(GroupsDialog.accept)
        self.buttonBox.rejected.connect(GroupsDialog.reject)

        QMetaObject.connectSlotsByName(GroupsDialog)
    # setupUi

    def retranslateUi(self, GroupsDialog):
        GroupsDialog.setWindowTitle(QCoreApplication.translate("GroupsDialog", u"Dialog", None))
        self.pushButtonAddGroup.setText(QCoreApplication.translate("GroupsDialog", u"Add Group", None))
        self.pushButtonDeleteGroup.setText(QCoreApplication.translate("GroupsDialog", u"Delete Group", None))
    # retranslateUi

