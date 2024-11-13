from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QActionGroup, QFont, QIcon, QKeySequence, Qt
from PySide6.QtPrintSupport import QPrintDialog
from PySide6.QtWidgets import QComboBox, QFileDialog, QFontComboBox, QToolBar, QWidget

from tse_analytics.core import messaging
from tse_analytics.css import style_descriptive_table
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.reports.reports_widget_ui import Ui_ReportsWidget

FONT_SIZES = [
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    18,
    24,
    36,
    48,
    64,
    72,
    96,
    144,
    288,
]


class ReportsWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_ReportsWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)
        messaging.subscribe(self, messaging.AddToReportMessage, self._add_to_report)

        self.ui.editor.textChanged.connect(self._report_changed)
        self.ui.editor.selectionChanged.connect(self._update_format)

        self.ui.editor.document().setDefaultStyleSheet(style_descriptive_table)

        toolbar = QToolBar("Editor Toolbar")
        toolbar.setIconSize(QSize(16, 16))

        new_action = QAction(QIcon(":/icons/icons8-file-16.png"), "New Report", self)
        new_action.setStatusTip("New report")
        new_action.triggered.connect(self._new_report)
        toolbar.addAction(new_action)

        save_action = QAction(QIcon(":/icons/icons8-save-16.png"), "Save", self)
        save_action.setStatusTip("Save current report")
        save_action.triggered.connect(self._save_report)
        toolbar.addAction(save_action)

        print_action = QAction(QIcon(":/icons/icons8-print-16.png"), "Print", self)
        print_action.setStatusTip("Print current report")
        print_action.triggered.connect(self._print)
        toolbar.addAction(print_action)

        toolbar.addSeparator()

        undo_action = QAction(
            QIcon(":/icons/icons8-undo-16.png"),
            "Undo",
            self,
        )
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.ui.editor.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction(
            QIcon(":/icons/icons8-redo-16.png"),
            "Redo",
            self,
        )
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.ui.editor.redo)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        cut_action = QAction(QIcon(":/icons/icons8-cut-16.png"), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.ui.editor.cut)
        toolbar.addAction(cut_action)

        copy_action = QAction(
            QIcon(":/icons/icons8-copy-16.png"),
            "Copy",
            self,
        )
        copy_action.setStatusTip("Copy selected text")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.ui.editor.copy)
        toolbar.addAction(copy_action)

        paste_action = QAction(
            QIcon(":/icons/icons8-paste-16.png"),
            "Paste",
            self,
        )
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.ui.editor.paste)
        toolbar.addAction(paste_action)

        toolbar.addSeparator()

        # We need references to these actions/settings to update as selection changes, so attach to self.
        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.ui.editor.setCurrentFont)
        toolbar.addWidget(self.fonts)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])

        # Connect to the signal producing the text of the current selection. Convert the string to float
        # and set as the pointsize. We could also use the index + retrieve from FONT_SIZES.
        self.fontsize.currentTextChanged.connect(lambda s: self.ui.editor.setFontPointSize(float(s)))
        toolbar.addWidget(self.fontsize)

        self.bold_action = QAction(QIcon(":/icons/icons8-bold-16.png"), "Bold", self)
        self.bold_action.setStatusTip("Bold")
        self.bold_action.setShortcut(QKeySequence.StandardKey.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.toggled.connect(
            lambda x: self.ui.editor.setFontWeight(QFont.Weight.Bold if x else QFont.Weight.Normal)
        )
        toolbar.addAction(self.bold_action)

        self.italic_action = QAction(
            QIcon(":/icons/icons8-italic-16.png"),
            "Italic",
            self,
        )
        self.italic_action.setStatusTip("Italic")
        self.italic_action.setShortcut(QKeySequence.StandardKey.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.toggled.connect(self.ui.editor.setFontItalic)
        toolbar.addAction(self.italic_action)

        self.underline_action = QAction(
            QIcon(":/icons/icons8-underline-16.png"),
            "Underline",
            self,
        )
        self.underline_action.setStatusTip("Underline")
        self.underline_action.setShortcut(QKeySequence.StandardKey.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.toggled.connect(self.ui.editor.setFontUnderline)
        toolbar.addAction(self.underline_action)

        toolbar.addSeparator()

        self.alignl_action = QAction(
            QIcon(":/icons/icons8-align-left-16.png"),
            "Align left",
            self,
        )
        self.alignl_action.setStatusTip("Align text left")
        self.alignl_action.setCheckable(True)
        self.alignl_action.triggered.connect(lambda: self.ui.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        toolbar.addAction(self.alignl_action)

        self.alignc_action = QAction(
            QIcon(":/icons/icons8-align-center-16.png"),
            "Align center",
            self,
        )
        self.alignc_action.setStatusTip("Align text center")
        self.alignc_action.setCheckable(True)
        self.alignc_action.triggered.connect(lambda: self.ui.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        toolbar.addAction(self.alignc_action)

        self.alignr_action = QAction(
            QIcon(":/icons/icons8-align-right-16.png"),
            "Align right",
            self,
        )
        self.alignr_action.setStatusTip("Align text right")
        self.alignr_action.setCheckable(True)
        self.alignr_action.triggered.connect(lambda: self.ui.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        toolbar.addAction(self.alignr_action)

        self.alignj_action = QAction(
            QIcon(":/icons/icons8-align-justify-16.png"),
            "Justify",
            self,
        )
        self.alignj_action.setStatusTip("Justify text")
        self.alignj_action.setCheckable(True)
        self.alignj_action.triggered.connect(lambda: self.ui.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        toolbar.addAction(self.alignj_action)

        format_group = QActionGroup(self)
        format_group.setExclusive(True)
        format_group.addAction(self.alignl_action)
        format_group.addAction(self.alignc_action)
        format_group.addAction(self.alignr_action)
        format_group.addAction(self.alignj_action)

        toolbar.addSeparator()

        # A list of all format-related widgets/actions, so we can disable/enable signals when updating.
        self._format_actions = [
            self.fonts,
            self.fontsize,
            self.bold_action,
            self.italic_action,
            self.underline_action,
            # We don't need to disable signals for alignment, as they are paragraph-wide.
        ]

        self.layout().insertWidget(0, toolbar)

        # Initialize.
        self._update_format()

        self.dataset: Dataset | None = None

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        self.dataset = message.dataset
        if self.dataset is not None:
            self.ui.editor.document().setHtml(self.dataset.report)

    def _add_to_report(self, message: messaging.AddToReportMessage):
        self.ui.editor.append(message.content)

    def _new_report(self):
        self.ui.editor.document().clear()

    def _report_changed(self):
        if self.dataset is not None:
            self.dataset.report = self.ui.editor.toHtml()

    def _print(self):
        dlg = QPrintDialog()
        if dlg.exec():
            self.ui.editor.document().print_(dlg.printer())

    def _save_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "HTML Files (*.html)")
        if filename:
            with open(filename, "w") as file:
                file.write(self.ui.editor.document().toHtml())

            # printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            # printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            # printer.setOutputFileName(filename)
            # # doc.setPageSize(printer.pageRect().size()); // This is necessary if you want to hide the page number
            # self.ui.textEdit.document().print_(printer)

    def _block_signals(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def _update_format(self):
        """
        Update the font format toolbar/actions when a new text selection is made. This is necessary to keep
        toolbars/etc. in sync with the current edit state.
        :return:
        """
        # Disable signals for all format widgets, so changing values here does not trigger further formatting.
        self._block_signals(self._format_actions, True)

        self.fonts.setCurrentFont(self.ui.editor.currentFont())
        # Nasty, but we get the font-size as a float but want it was an int
        self.fontsize.setCurrentText(str(int(self.ui.editor.fontPointSize())))

        self.italic_action.setChecked(self.ui.editor.fontItalic())
        self.underline_action.setChecked(self.ui.editor.fontUnderline())
        self.bold_action.setChecked(self.ui.editor.fontWeight() == QFont.Weight.Bold)

        self.alignl_action.setChecked(self.ui.editor.alignment() == Qt.AlignmentFlag.AlignLeft)
        self.alignc_action.setChecked(self.ui.editor.alignment() == Qt.AlignmentFlag.AlignCenter)
        self.alignr_action.setChecked(self.ui.editor.alignment() == Qt.AlignmentFlag.AlignRight)
        self.alignj_action.setChecked(self.ui.editor.alignment() == Qt.AlignmentFlag.AlignJustify)

        self._block_signals(self._format_actions, False)
