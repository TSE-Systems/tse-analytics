# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QStatusBar, QTabWidget,
    QToolBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1080, 713)
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
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayoutCentral = QVBoxLayout(self.centralWidget)
        self.verticalLayoutCentral.setObjectName(u"verticalLayoutCentral")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(False)

        self.verticalLayoutCentral.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1080, 21))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.dockWidgetDatasets = QDockWidget(MainWindow)
        self.dockWidgetDatasets.setObjectName(u"dockWidgetDatasets")
        self.widgetDatasets = QWidget()
        self.widgetDatasets.setObjectName(u"widgetDatasets")
        self.verticalLayoutOverview = QVBoxLayout(self.widgetDatasets)
        self.verticalLayoutOverview.setObjectName(u"verticalLayoutOverview")
        self.dockWidgetDatasets.setWidget(self.widgetDatasets)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetDatasets)
        self.dockWidgetSelection = QDockWidget(MainWindow)
        self.dockWidgetSelection.setObjectName(u"dockWidgetSelection")
        self.widgetSelection = QWidget()
        self.widgetSelection.setObjectName(u"widgetSelection")
        self.verticalLayoutSelection = QVBoxLayout(self.widgetSelection)
        self.verticalLayoutSelection.setObjectName(u"verticalLayoutSelection")
        self.tabWidgetSelection = QTabWidget(self.widgetSelection)
        self.tabWidgetSelection.setObjectName(u"tabWidgetSelection")
        self.tabWidgetSelection.setMovable(True)

        self.verticalLayoutSelection.addWidget(self.tabWidgetSelection)

        self.dockWidgetSelection.setWidget(self.widgetSelection)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidgetSelection)
        self.dockWidgetInfo = QDockWidget(MainWindow)
        self.dockWidgetInfo.setObjectName(u"dockWidgetInfo")
        self.widgetInfo = QWidget()
        self.widgetInfo.setObjectName(u"widgetInfo")
        self.verticalLayoutInfo = QVBoxLayout(self.widgetInfo)
        self.verticalLayoutInfo.setObjectName(u"verticalLayoutInfo")
        self.dockWidgetInfo.setWidget(self.widgetInfo)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidgetInfo)
        self.dockWidgetSettings = QDockWidget(MainWindow)
        self.dockWidgetSettings.setObjectName(u"dockWidgetSettings")
        self.widgetSettings = QWidget()
        self.widgetSettings.setObjectName(u"widgetSettings")
        self.verticalLayoutSettings = QVBoxLayout(self.widgetSettings)
        self.verticalLayoutSettings.setObjectName(u"verticalLayoutSettings")
        self.dockWidgetSettings.setWidget(self.widgetSettings)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidgetSettings)
        self.dockWidgetSelection.raise_()
        self.dockWidgetInfo.raise_()
        self.dockWidgetSettings.raise_()

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpenWorkspace)
        self.menuFile.addAction(self.actionSaveWorkspace)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImportDataset)
        self.menuFile.addAction(self.actionExportExcel)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.toolBar.addAction(self.actionOpenWorkspace)
        self.toolBar.addAction(self.actionSaveWorkspace)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionImportDataset)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(-1)


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
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"ToolBar", None))
        self.dockWidgetDatasets.setWindowTitle(QCoreApplication.translate("MainWindow", u"Datasets", None))
        self.dockWidgetSelection.setWindowTitle(QCoreApplication.translate("MainWindow", u"Selection", None))
        self.dockWidgetInfo.setWindowTitle(QCoreApplication.translate("MainWindow", u"Info", None))
        self.dockWidgetSettings.setWindowTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

