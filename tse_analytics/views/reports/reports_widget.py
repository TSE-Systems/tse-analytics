from pypdf import PdfWriter
from PySide6.QtCore import QDir, QTemporaryFile
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QFileDialog, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.reports.reports_widget_ui import Ui_ReportsWidget


class ReportsWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_ReportsWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonClear.clicked.connect(self.__clear_report)
        self.ui.pushButtonExport.clicked.connect(self.__export_report)

        self.ui.pdfView.setPageMode(QPdfView.PageMode.MultiPage)

        self.report_file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.pdf", self)
        self.pdf_writer = PdfWriter()
        self.pdf_document = QPdfDocument(self)
        self.ui.pdfView.setDocument(self.pdf_document)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, AddToReportMessage, self.__add_to_report)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear_report()

    def __add_to_report(self, message: AddToReportMessage):
        for pdf_file in message.pdf_file_names:
            self.pdf_writer.append(pdf_file)
        if self.report_file.open():
            self.pdf_writer.write(self.report_file.fileName())
        # self.pdf_writer.close()
        self.pdf_document.load(self.report_file.fileName())

    def __clear_report(self):
        self.pdf_writer = PdfWriter()
        if self.report_file.open():
            self.pdf_writer.write(self.report_file.fileName())
        self.pdf_document.load(self.report_file.fileName())

    def __export_report(self):
        if len(self.pdf_writer.pages) > 0:
            filename, _ = QFileDialog.getSaveFileName(self, "Export report", "", "PDF Files (*.pdf)")
            if filename:
                self.pdf_writer.write(filename)
                self.pdf_writer.close()
