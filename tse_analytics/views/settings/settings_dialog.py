from matplotlib import rcParams
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.settings.settings_dialog_ui import Ui_SettingsDialog


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        settings = QSettings()

        help_mode = settings.value("HelpMode", "online")
        if help_mode == "online":
            self.ui.radioButtonOnline.setChecked(True)
        else:
            self.ui.radioButtonOffline.setChecked(True)

        dpi = float(settings.value("DPI", 96))
        self.ui.dpiSpinBox.setValue(dpi)

        figure_width = float(settings.value("FigureWidth", 6.4))
        self.ui.figureWidthInchesDoubleSpinBox.setValue(figure_width)

        figure_height = float(settings.value("FigureHeight", 4.8))
        self.ui.figureHeightInchesDoubleSpinBox.setValue(figure_height)

        self.ui.buttonBox.accepted.connect(self._accepted)

    def _accepted(self) -> None:
        settings = QSettings()

        settings.setValue("HelpMode", "online" if self.ui.radioButtonOnline.isChecked() else "offline")

        settings.setValue("DPI", self.ui.dpiSpinBox.value())
        settings.setValue("FigureWidth", self.ui.figureWidthInchesDoubleSpinBox.value())
        settings.setValue("FigureHeight", self.ui.figureHeightInchesDoubleSpinBox.value())

        rcParams["figure.dpi"] = self.ui.dpiSpinBox.value()
        rcParams["figure.figsize"] = (
            self.ui.figureWidthInchesDoubleSpinBox.value(),
            self.ui.figureHeightInchesDoubleSpinBox.value(),
        )
