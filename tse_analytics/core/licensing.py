import codecs
import json
import shutil
from dataclasses import dataclass
import subprocess
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QStandardPaths
from cryptography.fernet import Fernet


LICENSE_FILENAME = "tse-analytics.license"


def get_hardware_id() -> str:
    ps_args = "-Command (Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"

    cmd = ["powershell", *ps_args.split(" ")]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, _ = proc.communicate(timeout=120)

    raw_output = out.decode("utf-8").strip()
    return raw_output


@dataclass
class License:
    HardwareId: str
    OwnerName: str
    OwnerCompany: str
    OwnerEmail: str
    Features: list[str]
    ExpirationDate: Optional[str] = None


class LicenseManager:
    key = "LXP9fAdogHWuqwbBrZDIUii830rEJpGtfjaadnznxWN="
    license: Optional[License] = None

    @staticmethod
    def load_license():
        license_path = (
            Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
            / LICENSE_FILENAME
        )
        if not license_path.is_file():
            return

        fernet = Fernet(codecs.decode(LicenseManager.key, "rot13"))

        with open(license_path, "rb") as f:
            token = f.read()

        payload = fernet.decrypt(token)
        data = json.loads(payload)

        LicenseManager.license = License(**data)

    @staticmethod
    def register_license(path: str):
        original_path = Path(path)
        if not original_path.is_file():
            return

        license_path = (
            Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
            / LICENSE_FILENAME
        )
        shutil.copy(original_path, license_path)
        LicenseManager.load_license()

    @staticmethod
    def is_feature_available(feature: str) -> bool:
        if LicenseManager.license is None:
            return False
        else:
            return feature in LicenseManager.license.Features
