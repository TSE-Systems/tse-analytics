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

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, AddToReportMessage, self.__add_to_report)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear_report()

    def __add_to_report(self, message: AddToReportMessage):
        self.ui.textEdit.append(message.content)

    def __clear_report(self):
        self.ui.textEdit.clear()

    def __export_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export report", "", "HTML Files (*.html)")
        if filename:
            with open(filename, "w") as file:
                file.write(self.ui.textEdit.toHtml())

            # printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            # printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            # printer.setOutputFileName(filename)
            # # doc.setPageSize(printer.pageRect().size()); // This is necessary if you want to hide the page number
            # self.ui.textEdit.document().print_(printer)
