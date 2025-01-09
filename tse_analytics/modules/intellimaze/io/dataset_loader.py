import glob
import tempfile
import timeit
import zipfile
from pathlib import Path

import pandas as pd
import xmltodict
from loguru import logger

from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellimaze.animalgate.io.animalgate_loader import load_animalgate_data
from tse_analytics.modules.intellimaze.data.im_dataset import IMDataset


def import_im_dataset(path: Path) -> IMDataset | None:
    tic = timeit.default_timer()

    if not zipfile.is_zipfile(path):
        return None

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
            animals = _import_animals(tmp_path / "Animals" / "Animals.animals")

            experiment_filename = metadata["ExperimentFilename"]
            dataset = IMDataset(
                name=Path(experiment_filename).stem,
                path=str(path),
                meta={
                    "experiment": metadata,
                    "animals": {k: v.get_dict() for (k, v) in animals.items()},
                },
                animals=animals,
                variables={},
                df=pd.DataFrame(),
                sampling_interval=pd.to_timedelta(1, unit="s"),
            )

            if (tmp_path / "AnimalGate").is_dir():
                dataset.animalgate_data = load_animalgate_data(tmp_path / "AnimalGate", dataset)

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


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
            text1=item["Sex"],
            text2=item["Strain"],
            text3=item["Group"],
        )
        animals[animal.id] = animal
    return animals
