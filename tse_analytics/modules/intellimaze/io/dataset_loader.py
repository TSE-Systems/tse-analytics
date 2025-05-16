import glob
import tempfile
import timeit
import zipfile
from pathlib import Path

import pandas as pd
import xmltodict
from loguru import logger

from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.data.utils import preprocess_main_table
from tse_analytics.modules.intellimaze.extensions import animal_gate, consumption_scale, running_wheel

extension_data_loaders = {
    animal_gate.EXTENSION_NAME: animal_gate.io.import_data,
    consumption_scale.EXTENSION_NAME: consumption_scale.io.import_data,
    running_wheel.EXTENSION_NAME: running_wheel.io.import_data,
}


def import_intellimaze_dataset(path: Path) -> IntelliMazeDataset | None:
    tic = timeit.default_timer()

    with zipfile.ZipFile(path, mode="r") as zip:
        with tempfile.TemporaryDirectory(prefix="tse-analytics-") as tempdir:
            tmp_path = Path(tempdir)
            zip.extractall(tempdir)

            protocols_files = glob.glob(
                "*.IntelliMaze",
                root_dir=tmp_path,
            )
            if len(protocols_files) != 1:
                # TODO: Not IntelliMaze archive!
                return None

            metadata = _import_metadata(tmp_path / "Info.xml")
            devices = _get_devices(metadata)

            if (tmp_path / "Groups").is_dir():
                animals = _import_animals_v6(tmp_path / "Animals" / "Animals.animals")
            else:
                animals = _import_animals_v5(tmp_path / "Animals" / "Animals.animals")

            dataset = IntelliMazeDataset(
                metadata={
                    "name": path.stem,
                    "description": "IntelliMaze dataset",
                    "source_path": str(path),
                    "experiment_started": str(
                        pd.to_datetime(metadata["ExperimentStarted"], format="%m/%d/%Y %H:%M:%S")
                    ),
                    "experiment_stopped": str(
                        pd.to_datetime(metadata["ExperimentStopped"], format="%m/%d/%Y %H:%M:%S")
                    ),
                    "experiment": metadata,
                    "animals": {k: v.get_dict() for (k, v) in animals.items()},
                },
                animals=animals,
                devices=devices,
            )

            for extension_name, data_loader in extension_data_loaders.items():
                if extension_name in devices and (tmp_path / extension_name).is_dir():
                    dataset.extensions_data[extension_name] = data_loader(tmp_path / extension_name, dataset)

    preprocess_main_table(dataset)

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _get_devices(metadata: dict) -> dict[str, list[str]]:
    devices = {}
    for item in metadata["Components"]["ComponentInfo"]:
        extension_name = item["Extension"]
        if extension_name not in devices:
            devices[extension_name] = []
        devices[extension_name].append(item["DeviceID"])

    # Sort by DeviceID
    for extension in devices.values():
        extension.sort()
    return devices


def _import_metadata(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["ExperimentInfo"]


def _import_animals_v5(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        json = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    animals = {}
    for index, item in enumerate(json["ArrayOfAnimal"]["Animal"]):
        properties = {
            "Tag": item["Tag"],
            "PMBoxNr": int(item["PMBoxNr"]),
            "Sex": item["Sex"] if "Sex" in item else "",
            "Strain": item["Strain"] if "Strain" in item else "",
            "Group": item["Group"] if "Group" in item else "",
            "Treatment": item["Treatment"] if "Treatment" in item else "",
            "Dosage": item["Dosage"] if "Dosage" in item else "",
            "Weight": float(item["Weight"]),
            "Age": item["Age"],
            "Notes": item["Notes"] if "Notes" in item else "",
        }

        animal = Animal(
            enabled=True,
            id=str(item["Name"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal
    return animals


def _import_animals_v6(path: Path) -> dict | None:
    # Data format starting from IntelliMaze 6.x
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        json = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    animals = {}
    for index, item in enumerate(json["ArrayOfAnimal"]["Animal"]):
        properties = {
            "Tag": item["Tag"],
            "PMBoxNr": int(item["PMBoxNr"]),
            "Sex": item["Sex"] if "Sex" in item else "",
            "Strain": item["Strain"] if "Strain" in item else "",
            "Group": item["Group"] if "Group" in item else "",
            "Treatment": item["Treatment"] if "Treatment" in item else "",
            "Dosage": item["Dosage"] if "Dosage" in item else "",
            "Weight": float(item["Weight"]),
            "Age": item["Age"],
            "Notes": item["Notes"] if "Notes" in item else "",
        }

        animal = Animal(
            enabled=True,
            id=str(item["Name"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal
    return animals
