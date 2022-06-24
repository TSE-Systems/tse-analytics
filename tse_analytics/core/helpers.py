from PySide6.QtWidgets import QMessageBox


def report_error(message: str, detail: str):
    """
    Display an error in a modal

    :param message: A short description of the error
    :type message: str
    :param detail: A longer description
    :type detail: str
    """
    qmb = QMessageBox(QMessageBox.Critical, "Error", message)
    qmb.setDetailedText(detail)
    qmb.resize(400, qmb.size().height())
    qmb.exec_()
