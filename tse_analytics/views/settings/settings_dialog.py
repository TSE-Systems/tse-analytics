from matplotlib import rcParams
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.settings.settings_dialog_ui import Ui_SettingsDialog

CLAUDE_MODELS = [
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
]
DEFAULT_CLAUDE_MODEL = "claude-opus-4-7"


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

        api_key = str(settings.value("AnthropicApiKey", ""))
        self.ui.anthropicApiKeyLineEdit.setText(api_key)

        self.ui.claudeModelComboBox.addItems(CLAUDE_MODELS)
        default_model = str(settings.value("DefaultClaudeModel", DEFAULT_CLAUDE_MODEL))
        if default_model not in CLAUDE_MODELS:
            default_model = DEFAULT_CLAUDE_MODEL
        self.ui.claudeModelComboBox.setCurrentText(default_model)

        self.ui.buttonBox.accepted.connect(self._accepted)

    def _accepted(self) -> None:
        settings = QSettings()

        settings.setValue("HelpMode", "online" if self.ui.radioButtonOnline.isChecked() else "offline")

        settings.setValue("DPI", self.ui.dpiSpinBox.value())
        settings.setValue("FigureWidth", self.ui.figureWidthInchesDoubleSpinBox.value())
        settings.setValue("FigureHeight", self.ui.figureHeightInchesDoubleSpinBox.value())

        settings.setValue("AnthropicApiKey", self.ui.anthropicApiKeyLineEdit.text().strip())
        settings.setValue("DefaultClaudeModel", self.ui.claudeModelComboBox.currentText())

        rcParams["figure.dpi"] = self.ui.dpiSpinBox.value()
        rcParams["figure.figsize"] = (
            self.ui.figureWidthInchesDoubleSpinBox.value(),
            self.ui.figureHeightInchesDoubleSpinBox.value(),
        )
