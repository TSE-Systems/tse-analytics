import glob
import tempfile
import timeit
import zipfile
from pathlib import Path

import pandas as pd
import xmltodict
from loguru import logger

from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellimaze.submodules.animal_gate.io.importer import import_animalgate_data
from tse_analytics.modules.intellimaze.submodules.consumption_scale.io.importer import import_consumptionscale_data
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.data.main_table_helper import preprocess_main_table
from tse_analytics.modules.intellimaze.submodules.running_wheel.io.importer import import_runningwheel_data


def import_im_dataset(path: Path) -> IntelliMazeDataset | None:
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
            animals = _import_animals(tmp_path / "Animals" / "Animals.animals")

            dataset = IntelliMazeDataset(
                name=path.stem,
                path=str(path),
                meta={
                    "experiment": metadata,
                    "animals": {k: v.get_dict() for (k, v) in animals.items()},
                },
                devices=devices,
                animals=animals,
            )

            if "AnimalGate" in devices and (tmp_path / "AnimalGate").is_dir():
                dataset.animal_gate_data = import_animalgate_data(tmp_path / "AnimalGate", dataset)

            if "RunningWheel" in devices and (tmp_path / "RunningWheel").is_dir():
                dataset.running_wheel_data = import_runningwheel_data(tmp_path / "RunningWheel", dataset)

            if "ConsumptionScale" in devices and (tmp_path / "ConsumptionScale").is_dir():
                dataset.consumption_scale_data = import_consumptionscale_data(tmp_path / "ConsumptionScale", dataset)

    dataset = preprocess_main_table(dataset, pd.to_timedelta(1, unit="minute"))

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


def _import_animals(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        json = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    animals = {}
    for item in json["ArrayOfAnimal"]["Animal"]:
        animal = Animal(
            enabled=True,
            id=str(item["Name"]),
            box=int(item["PMBoxNr"]),
            weight=float(item["Weight"]),
            tag=item["Tag"],
            sex=item["Sex"],
            group=item["Group"],
            text1=item["Treatment"],
            text2=item["Strain"],
            text3=item["Notes"] if "Notes" in item else "",
        )
        animals[animal.id] = animal
    return animals
