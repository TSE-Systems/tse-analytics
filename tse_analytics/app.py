import sys

# import PySide6 before matplotlib
import matplotlib
from pyqtgraph import setConfigOptions
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from tse_analytics.core.manager import Manager
from tse_analytics.views.main_window import MainWindow

matplotlib.use("QtAgg")

# Global PyQtGraph settings
setConfigOptions(
    imageAxisOrder="row-major",
    foreground="d",
    background="w",
    leftButtonPan=True,
    antialias=False,
    useOpenGL=False,
)


class App(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.setStyle("Fusion")
        self.setOrganizationName("TSE Systems")
        self.setOrganizationDomain("http://www.tse-systems.com")
        self.setApplicationName("TSE Analytics")
        self.setWindowIcon(QIcon(":/icons/icons8-eukaryotic-cells-96.png"))

        f = QFile(":/style.qss")
        f.open(QFile.ReadOnly | QFile.Text)
        self.setStyleSheet(QTextStream(f).readAll())
        f.close()

        # DataManager singleton initialization
        Manager()


def main():
    # sys.argv.append("--disable-web-security")
    app = App(sys.argv)

    mw = MainWindow()
    mw.show()

    sys.exit(app.exec_())
