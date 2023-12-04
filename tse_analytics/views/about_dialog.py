import importlib.metadata
from typing import Optional

from PySide6.QtWidgets import QDialog, QWidget, QPushButton, QDialogButtonBox, QFileDialog

from tse_analytics.core.licensing import LicenseManager, License, get_hardware_id
from tse_analytics.views.about_dialog_ui import Ui_AboutDialog


class AboutDialog(QDialog, Ui_AboutDialog):
    """About Dialog"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)

        register_license_button = QPushButton("Register License...")
        register_license_button.clicked.connect(self.__register_license)
        self.buttonBox.addButton(register_license_button, QDialogButtonBox.ButtonRole.ActionRole)

        version = importlib.metadata.version("tse-analytics")
        self.labelVersion.setText(f"Version: {version}")

        hardware_id = get_hardware_id()
        self.lineEditHardwareId.setText(hardware_id)

        self.__update_license_info(LicenseManager.license)

    def __update_license_info(self, license: License):
        if license is None:
            return

        self.nameLineEdit.setText(license.OwnerName)
        self.companyLineEdit.setText(license.OwnerCompany)
        self.emailLineEdit.setText(license.OwnerEmail)
        if license.ExpirationDate is None:
            self.expirationLabel.hide()
            self.expirationLineEdit.hide()
        else:
            self.expirationLineEdit.setText(license.ExpirationDate)
            self.expirationLabel.show()
            self.expirationLineEdit.show()

    def __register_license(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select license file",
            "",
            "License Files (*.license)",
        )
        if path:
            LicenseManager.register_license(path)
            self.__update_license_info(LicenseManager.license)
