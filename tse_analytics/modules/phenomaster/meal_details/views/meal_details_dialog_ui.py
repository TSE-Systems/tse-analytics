# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'meal_details_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QSizePolicy, QSpacerItem, QSplitter,
    QTabWidget, QToolBox, QToolButton, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_MealDetailsDialog(object):
    def setupUi(self, MealDetailsDialog):
        if not MealDetailsDialog.objectName():
            MealDetailsDialog.setObjectName(u"MealDetailsDialog")
        MealDetailsDialog.resize(1020, 854)
        self.verticalLayout = QVBoxLayout(MealDetailsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.toolButtonCalculate = QToolButton(MealDetailsDialog)
        self.toolButtonCalculate.setObjectName(u"toolButtonCalculate")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-scales-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonCalculate.setIcon(icon)
        self.toolButtonCalculate.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.toolbarLayout.addWidget(self.toolButtonCalculate)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.horizontalSpacer)

        self.toolButtonHelp = QToolButton(MealDetailsDialog)
        self.toolButtonHelp.setObjectName(u"toolButtonHelp")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toolButtonHelp.setIcon(icon1)

        self.toolbarLayout.addWidget(self.toolButtonHelp)


        self.verticalLayout.addLayout(self.toolbarLayout)

        self.splitter = QSplitter(MealDetailsDialog)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.splitter.addWidget(self.tabWidget)
        self.toolBox = QToolBox(self.splitter)
        self.toolBox.setObjectName(u"toolBox")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 870, 746))
        self.toolBox.addItem(self.page, u"Page 1")
        self.splitter.addWidget(self.toolBox)

        self.verticalLayout.addWidget(self.splitter)

        self.buttonBox = QDialogButtonBox(MealDetailsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(MealDetailsDialog)
        self.buttonBox.accepted.connect(MealDetailsDialog.accept)
        self.buttonBox.rejected.connect(MealDetailsDialog.reject)

        self.tabWidget.setCurrentIndex(-1)
        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MealDetailsDialog)
    # setupUi

    def retranslateUi(self, MealDetailsDialog):
        MealDetailsDialog.setWindowTitle(QCoreApplication.translate("MealDetailsDialog", u"Meal Details", None))
        self.toolButtonCalculate.setText(QCoreApplication.translate("MealDetailsDialog", u"Calculate", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("MealDetailsDialog", u"Page 1", None))
    # retranslateUi

