import tempfile
import timeit
import zipfile
from pathlib import Path

import pandas as pd
import xmltodict
from loguru import logger

from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellicage.data.ic_dataset import ICDataset
from tse_analytics.modules.intellicage.io.importer import import_intellicage_data


def import_ic_dataset(path: Path) -> ICDataset | None:
    tic = timeit.default_timer()

    with zipfile.ZipFile(path, mode="r") as zip:
        with tempfile.TemporaryDirectory(prefix="tse-analytics-") as tempdir:
            tmp_path = Path(tempdir)
            zip.extractall(tempdir)

            data_descriptor = _import_data_descriptor(tmp_path / "DataDescriptor.xml")
            metadata = _import_metadata(tmp_path / "Sessions.xml")
            animals = _import_animals(tmp_path / "Animals.txt")

            dataset = ICDataset(
                name=path.stem,
                path=str(path),
                meta={
                    "data_descriptor": data_descriptor,
                    "experiment": metadata,
                    "animals": {k: v.get_dict() for (k, v) in animals.items()},
                },
                animals=animals,
            )

            dataset.intelli_cage_data = import_intellicage_data(tmp_path / "IntelliCage", dataset)

    # dataset = preprocess_main_table(dataset, pd.to_timedelta(1, unit="minute"))

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


def _import_metadata(path: Path) -> dict | None:
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["ArrayOfSession"]["Session"]


def _import_animals(path: Path) -> dict | None:
    if not path.is_file():
        return None

    dtype = {
        "AnimalName": str,
        "AnimalTag": str,
        "Sex": str,
        "GroupName": str,
        "AnimalNotes": str,
    }

    df = pd.read_csv(
        path,
        delimiter="\t",
        decimal=".",
        dtype=dtype,
    )

    animals = {}
    for index, row in df.iterrows():
        animal = Animal(
            enabled=True,
            id=str(row["AnimalName"]),
            box=None,
            weight=None,
            text1=row["AnimalTag"],
            text2=row["GroupName"],
            text3=row["AnimalNotes"],
        )
        animals[animal.id] = animal

    return animals
