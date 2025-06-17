# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'place_preference_settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QLabel,
    QRadioButton, QSizePolicy, QVBoxLayout, QWidget)
import resources_rc

class Ui_PlacePreferencesSettingsWidget(object):
    def setupUi(self, PlacePreferencesSettingsWidget):
        if not PlacePreferencesSettingsWidget.objectName():
            PlacePreferencesSettingsWidget.setObjectName(u"PlacePreferencesSettingsWidget")
        self.verticalLayout = QVBoxLayout(PlacePreferencesSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxCorrectPlace = QGroupBox(PlacePreferencesSettingsWidget)
        self.groupBoxCorrectPlace.setObjectName(u"groupBoxCorrectPlace")
        self.verticalLayout_7 = QVBoxLayout(self.groupBoxCorrectPlace)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.checkBoxCorrect = QCheckBox(self.groupBoxCorrectPlace)
        self.checkBoxCorrect.setObjectName(u"checkBoxCorrect")
        self.checkBoxCorrect.setChecked(True)

        self.verticalLayout_7.addWidget(self.checkBoxCorrect)

        self.checkBoxNeutral = QCheckBox(self.groupBoxCorrectPlace)
        self.checkBoxNeutral.setObjectName(u"checkBoxNeutral")

        self.verticalLayout_7.addWidget(self.checkBoxNeutral)

        self.checkBoxIncorrect = QCheckBox(self.groupBoxCorrectPlace)
        self.checkBoxIncorrect.setObjectName(u"checkBoxIncorrect")

        self.verticalLayout_7.addWidget(self.checkBoxIncorrect)

        self.labelCorrectPlace = QLabel(self.groupBoxCorrectPlace)
        self.labelCorrectPlace.setObjectName(u"labelCorrectPlace")
        self.labelCorrectPlace.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.labelCorrectPlace.setWordWrap(True)

        self.verticalLayout_7.addWidget(self.labelCorrectPlace)


        self.verticalLayout.addWidget(self.groupBoxCorrectPlace)

        self.groupBoxExcludeCondition = QGroupBox(PlacePreferencesSettingsWidget)
        self.groupBoxExcludeCondition.setObjectName(u"groupBoxExcludeCondition")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxExcludeCondition)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.radioButtonNone = QRadioButton(self.groupBoxExcludeCondition)
        self.radioButtonNone.setObjectName(u"radioButtonNone")
        self.radioButtonNone.setChecked(True)

        self.verticalLayout_6.addWidget(self.radioButtonNone)

        self.radioButtonCorrect = QRadioButton(self.groupBoxExcludeCondition)
        self.radioButtonCorrect.setObjectName(u"radioButtonCorrect")

        self.verticalLayout_6.addWidget(self.radioButtonCorrect)

        self.radioButtonIncorrect = QRadioButton(self.groupBoxExcludeCondition)
        self.radioButtonIncorrect.setObjectName(u"radioButtonIncorrect")

        self.verticalLayout_6.addWidget(self.radioButtonIncorrect)

        self.labelExcludeCondition = QLabel(self.groupBoxExcludeCondition)
        self.labelExcludeCondition.setObjectName(u"labelExcludeCondition")
        self.labelExcludeCondition.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.labelExcludeCondition.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.labelExcludeCondition)


        self.verticalLayout.addWidget(self.groupBoxExcludeCondition)

        self.checkBoxVisitsWithNosepokes = QCheckBox(PlacePreferencesSettingsWidget)
        self.checkBoxVisitsWithNosepokes.setObjectName(u"checkBoxVisitsWithNosepokes")

        self.verticalLayout.addWidget(self.checkBoxVisitsWithNosepokes)

        self.checkBoxVisitsWithLicks = QCheckBox(PlacePreferencesSettingsWidget)
        self.checkBoxVisitsWithLicks.setObjectName(u"checkBoxVisitsWithLicks")

        self.verticalLayout.addWidget(self.checkBoxVisitsWithLicks)


        self.retranslateUi(PlacePreferencesSettingsWidget)

        QMetaObject.connectSlotsByName(PlacePreferencesSettingsWidget)
    # setupUi

    def retranslateUi(self, PlacePreferencesSettingsWidget):
        self.groupBoxCorrectPlace.setTitle(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Correct Place", None))
        self.checkBoxCorrect.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Correct", None))
        self.checkBoxNeutral.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Neutral", None))
        self.checkBoxIncorrect.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Incorrect", None))
        self.labelCorrectPlace.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Assign corner condition(s) that is representing correct responses, if the original assignment does not concur with the intended one. For instance, you might have coded incorrect visits as Neutral instead of Incorrect in the Experimental design.", None))
        self.groupBoxExcludeCondition.setTitle(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Exclude Condition", None))
        self.radioButtonNone.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"None", None))
        self.radioButtonCorrect.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Correct", None))
        self.radioButtonIncorrect.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Incorrect", None))
        self.labelExcludeCondition.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Exclude a corner condition, in case preference assessment is restricted to only two of the possible three conditions. For instance, there might be a correct and an incorrect choice in some corner(s), but some corner might not have been taken for conditioning and set to Neutral. Hence, you should exclude Neutral condition from learning analysis.", None))
        self.checkBoxVisitsWithNosepokes.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Include only visits with nosepokes", None))
        self.checkBoxVisitsWithLicks.setText(QCoreApplication.translate("PlacePreferencesSettingsWidget", u"Include only visits with licks", None))
        pass
    # retranslateUi

