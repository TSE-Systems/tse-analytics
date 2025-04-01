import tempfile
import timeit
import zipfile
from pathlib import Path

import xmltodict
from loguru import logger

from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellicage.io.dataset_loader_v1 import import_intellicage_dataset_v1
from tse_analytics.modules.intellicage.io.dataset_loader_v2 import import_intellicage_dataset_v2


def import_intellicage_dataset(path: Path) -> IntelliCageDataset | None:
    tic = timeit.default_timer()

    with zipfile.ZipFile(path, mode="r") as zip:
        with tempfile.TemporaryDirectory(prefix="tse-analytics-") as tempdir:
            tmp_path = Path(tempdir)
            zip.extractall(tempdir)

            data_descriptor = _import_data_descriptor(tmp_path / "DataDescriptor.xml")

            if data_descriptor["Version"] == "Version1":
                dataset = import_intellicage_dataset_v1(path, tmp_path, data_descriptor)
            else:
                dataset = import_intellicage_dataset_v2(path, tmp_path, data_descriptor)

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _import_data_descriptor(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["DataDescriptor"]
