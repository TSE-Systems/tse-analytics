import codecs
import json
import shutil
from dataclasses import dataclass
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QStandardPaths
from cryptography.fernet import Fernet, InvalidToken
from loguru import logger


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
    Features: list[str]
    OwnerName: Optional[str] = None
    OwnerCompany: Optional[str] = None
    OwnerEmail: Optional[str] = None
    ExpirationDate: Optional[str] = None


class LicenseManager:
    key = "LXP9fAdogHWuqwbBrZDIUii830rEJpGtfjaadnznxWN="
    license: Optional[License] = None
    hardware_id = get_hardware_id()

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

        try:
            payload = fernet.decrypt(token)
        except InvalidToken as error:
            logger.exception(error)
            return
        data = json.loads(payload)

        LicenseManager.license = License(**data)

    @staticmethod
    def register_license(path: str):
        original_path = Path(path)
        if not original_path.is_file():
            return

        license_path = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
        if not license_path.exists():
            license_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(original_path, license_path / LICENSE_FILENAME)
        LicenseManager.load_license()

    @staticmethod
    def is_license_missing() -> bool:
        return LicenseManager.license is None

    @staticmethod
    def is_license_expired() -> bool:
        if LicenseManager.license is None:
            return True

        if LicenseManager.license.ExpirationDate is None:
            return False

        expiration_date = datetime.strptime(LicenseManager.license.ExpirationDate, "%Y-%m-%d").date()
        return datetime.today().date() > expiration_date

    @staticmethod
    def is_hardware_id_invalid() -> bool:
        if LicenseManager.license is None:
            return True
        return LicenseManager.hardware_id != LicenseManager.license.HardwareId

    @staticmethod
    def is_feature_missing(feature: str) -> bool:
        if LicenseManager.license is None:
            return True
        else:
            return feature not in LicenseManager.license.Features
