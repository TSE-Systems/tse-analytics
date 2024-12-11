# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'time_phases_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QSizePolicy, QSpacerItem, QTableView,
    QToolButton, QVBoxLayout, QWidget)
import resources_rc

class Ui_TimePhasesSettingsWidget(object):
    def setupUi(self, TimePhasesSettingsWidget):
        if not TimePhasesSettingsWidget.objectName():
            TimePhasesSettingsWidget.setObjectName(u"TimePhasesSettingsWidget")
        self.verticalLayout = QVBoxLayout(TimePhasesSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxPhases = QGroupBox(TimePhasesSettingsWidget)
        self.groupBoxPhases.setObjectName(u"groupBoxPhases")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxPhases)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tableViewTimePhases = QTableView(self.groupBoxPhases)
        self.tableViewTimePhases.setObjectName(u"tableViewTimePhases")
        self.tableViewTimePhases.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableViewTimePhases.verticalHeader().setMinimumSectionSize(20)
        self.tableViewTimePhases.verticalHeader().setDefaultSectionSize(20)

        self.verticalLayout_2.addWidget(self.tableViewTimePhases)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.toolButtonAddPhase = QToolButton(self.groupBoxPhases)
        self.toolButtonAddPhase.setObjectName(u"toolButtonAddPhase")
        icon = QIcon()
        icon.addFile(u":/icons/icons8-add-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonAddPhase.setIcon(icon)

        self.horizontalLayout.addWidget(self.toolButtonAddPhase)

        self.toolButtonDeletePhase = QToolButton(self.groupBoxPhases)
        self.toolButtonDeletePhase.setObjectName(u"toolButtonDeletePhase")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-minus-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButtonDeletePhase.setIcon(icon1)

        self.horizontalLayout.addWidget(self.toolButtonDeletePhase)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBoxPhases)


        self.retranslateUi(TimePhasesSettingsWidget)

        QMetaObject.connectSlotsByName(TimePhasesSettingsWidget)
    # setupUi

    def retranslateUi(self, TimePhasesSettingsWidget):
        self.groupBoxPhases.setTitle(QCoreApplication.translate("TimePhasesSettingsWidget", u"Time Phases", None))
#if QT_CONFIG(tooltip)
        self.toolButtonAddPhase.setToolTip(QCoreApplication.translate("TimePhasesSettingsWidget", u"Add time phase", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.toolButtonDeletePhase.setToolTip(QCoreApplication.translate("TimePhasesSettingsWidget", u"Delete selected time phase", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

