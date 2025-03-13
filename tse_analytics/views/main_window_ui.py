# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QToolBar, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1120, 754)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon = QIcon()
        icon.addFile(u":/icons/exit.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionExit.setIcon(icon)
        self.actionExit.setShortcutVisibleInContextMenu(False)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon1 = QIcon()
        icon1.addFile(u":/icons/about-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionAbout.setIcon(icon1)
        self.actionImportDataset = QAction(MainWindow)
        self.actionImportDataset.setObjectName(u"actionImportDataset")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons8-import-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionImportDataset.setIcon(icon2)
        self.actionOpenWorkspace = QAction(MainWindow)
        self.actionOpenWorkspace.setObjectName(u"actionOpenWorkspace")
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons8-opened-folder-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOpenWorkspace.setIcon(icon3)
        self.actionSaveWorkspace = QAction(MainWindow)
        self.actionSaveWorkspace.setObjectName(u"actionSaveWorkspace")
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons8-save-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSaveWorkspace.setIcon(icon4)
        self.actionResetLayout = QAction(MainWindow)
        self.actionResetLayout.setObjectName(u"actionResetLayout")
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        icon5 = QIcon()
        icon5.addFile(u":/icons/icons8-help-16.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionHelp.setIcon(icon5)
        self.actionSaveLayout = QAction(MainWindow)
        self.actionSaveLayout.setObjectName(u"actionSaveLayout")
        self.actionSaveLayout.setMenuRole(QAction.MenuRole.NoRole)
        self.actionRestoreLayout = QAction(MainWindow)
        self.actionRestoreLayout.setObjectName(u"actionRestoreLayout")
        self.actionRestoreLayout.setMenuRole(QAction.MenuRole.NoRole)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1120, 21))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOpenRecent = QMenu(self.menuFile)
        self.menuOpenRecent.setObjectName(u"menuOpenRecent")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        self.menuStyle = QMenu(self.menuView)
        self.menuStyle.setObjectName(u"menuStyle")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpenWorkspace)
        self.menuFile.addAction(self.menuOpenRecent.menuAction())
        self.menuFile.addAction(self.actionSaveWorkspace)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImportDataset)
        self.menuFile.addSeparator()
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionSaveLayout)
        self.menuView.addAction(self.actionRestoreLayout)
        self.menuView.addAction(self.actionResetLayout)
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuStyle.menuAction())
        self.menuView.addSeparator()
        self.toolBar.addAction(self.actionOpenWorkspace)
        self.toolBar.addAction(self.actionSaveWorkspace)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionImportDataset)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"TSE Analytics", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"E&xit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionImportDataset.setText(QCoreApplication.translate("MainWindow", u"Import Dataset", None))
#if QT_CONFIG(tooltip)
        self.actionImportDataset.setToolTip(QCoreApplication.translate("MainWindow", u"Import dataset...", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenWorkspace.setText(QCoreApplication.translate("MainWindow", u"Open Workspace", None))
#if QT_CONFIG(tooltip)
        self.actionOpenWorkspace.setToolTip(QCoreApplication.translate("MainWindow", u"Open workspace...", None))
#endif // QT_CONFIG(tooltip)
        self.actionSaveWorkspace.setText(QCoreApplication.translate("MainWindow", u"Save Workspace", None))
#if QT_CONFIG(tooltip)
        self.actionSaveWorkspace.setToolTip(QCoreApplication.translate("MainWindow", u"Save workspace...", None))
#endif // QT_CONFIG(tooltip)
        self.actionResetLayout.setText(QCoreApplication.translate("MainWindow", u"Reset Layout", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionSaveLayout.setText(QCoreApplication.translate("MainWindow", u"Save Layout", None))
        self.actionRestoreLayout.setText(QCoreApplication.translate("MainWindow", u"Restore Layout", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuOpenRecent.setTitle(QCoreApplication.translate("MainWindow", u"Open Recent", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"&View", None))
        self.menuStyle.setTitle(QCoreApplication.translate("MainWindow", u"Style", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"ToolBar", None))
    # retranslateUi

