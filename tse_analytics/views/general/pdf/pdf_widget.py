from io import BytesIO

from PySide6.QtCore import QSize, Qt, QBuffer, QIODevice, QByteArray
from PySide6.QtGui import QIcon
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QFileDialog


class PdfWidget(QWidget):
    def __init__(self, pdf_bytes: BytesIO, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle("PDF Viewer")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar(
            "PDF Widget Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.toolbar.addAction(QIcon(":/icons/icons8-export-16.png"), "Export PDF").triggered.connect(self._export_pdf)
        self._layout.addWidget(self.toolbar)

        self.pdf_document = QPdfDocument(self)

        self.buffer = QBuffer()
        self.buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        self.buffer.write(QByteArray(pdf_bytes.getvalue()))
        self.buffer.seek(0)

        self.pdf_document.load(self.buffer)

        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.pdf_document)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)

        self._layout.addWidget(self.pdf_view)

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
        if file_path:
            with open(file_path, "wb") as file:
                self.buffer.seek(0)
                pdf_data = self.buffer.data()
                file.write(pdf_data)

    def sizeHint(self) -> QSize:
        return QSize(900, 800)
