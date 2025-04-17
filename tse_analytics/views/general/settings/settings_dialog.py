from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.general.settings.settings_dialog_ui import Ui_SettingsDialog


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self.settings = QSettings()

        help_mode = self.settings.value("HelpMode", "online")
        if help_mode == "online":
            self.radioButtonOnline.setChecked(True)
        else:
            self.radioButtonOffline.setChecked(True)

        self.radioButtonOnline.toggled.connect(
            lambda toggled: self.settings.setValue("HelpMode", "online") if toggled else None
        )
        self.radioButtonOffline.toggled.connect(
            lambda toggled: self.settings.setValue("HelpMode", "offline") if toggled else None
        )
