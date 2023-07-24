# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
        MainWindow.resize(1472, 1032)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon = QIcon()
        icon.addFile(u":/icons/exit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionExit.setIcon(icon)
        self.actionExit.setShortcutVisibleInContextMenu(False)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons8-about-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionAbout.setIcon(icon1)
        self.actionImportDataset = QAction(MainWindow)
        self.actionImportDataset.setObjectName(u"actionImportDataset")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons8-import-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionImportDataset.setIcon(icon2)
        self.actionOpenWorkspace = QAction(MainWindow)
        self.actionOpenWorkspace.setObjectName(u"actionOpenWorkspace")
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons8-opened-folder-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionOpenWorkspace.setIcon(icon3)
        self.actionSaveWorkspace = QAction(MainWindow)
        self.actionSaveWorkspace.setObjectName(u"actionSaveWorkspace")
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons8-save-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionSaveWorkspace.setIcon(icon4)
        self.actionExportExcel = QAction(MainWindow)
        self.actionExportExcel.setObjectName(u"actionExportExcel")
        icon5 = QIcon()
        icon5.addFile(u":/icons/icons8-export-16.png", QSize(), QIcon.Normal, QIcon.Off)
        self.actionExportExcel.setIcon(icon5)
        self.actionResetLayout = QAction(MainWindow)
        self.actionResetLayout.setObjectName(u"actionResetLayout")
        self.actionewfw = QAction(MainWindow)
        self.actionewfw.setObjectName(u"actionewfw")
        self.actionExportCsv = QAction(MainWindow)
        self.actionExportCsv.setObjectName(u"actionExportCsv")
        self.actionExportCsv.setIcon(icon5)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1472, 22))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOpenRecent = QMenu(self.menuFile)
        self.menuOpenRecent.setObjectName(u"menuOpenRecent")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpenWorkspace)
        self.menuFile.addAction(self.menuOpenRecent.menuAction())
        self.menuFile.addAction(self.actionSaveWorkspace)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImportDataset)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExportExcel)
        self.menuFile.addAction(self.actionExportCsv)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionResetLayout)
        self.toolBar.addAction(self.actionOpenWorkspace)
        self.toolBar.addAction(self.actionSaveWorkspace)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionImportDataset)
        self.toolBar.addSeparator()

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
        self.actionExportExcel.setText(QCoreApplication.translate("MainWindow", u"Export to Excel", None))
#if QT_CONFIG(tooltip)
        self.actionExportExcel.setToolTip(QCoreApplication.translate("MainWindow", u"Export to Excel...", None))
#endif // QT_CONFIG(tooltip)
        self.actionResetLayout.setText(QCoreApplication.translate("MainWindow", u"Reset Layout", None))
        self.actionewfw.setText(QCoreApplication.translate("MainWindow", u"ewfw", None))
        self.actionExportCsv.setText(QCoreApplication.translate("MainWindow", u"Export to CSV", None))
#if QT_CONFIG(tooltip)
        self.actionExportCsv.setToolTip(QCoreApplication.translate("MainWindow", u"Export to CSV...", None))
#endif // QT_CONFIG(tooltip)
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuOpenRecent.setTitle(QCoreApplication.translate("MainWindow", u"Open Recent", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"&View", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"ToolBar", None))
    # retranslateUi

