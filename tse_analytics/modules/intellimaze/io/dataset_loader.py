import glob
import tempfile
import timeit
import zipfile
from pathlib import Path

import pandas as pd
import xmltodict
from loguru import logger

from tse_analytics.core.color_manager import get_color_hex
from tse_analytics.core.data.shared import Animal, Factor
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.data.utils import preprocess_main_table
from tse_analytics.modules.intellimaze.extensions import animal_gate, consumption_scale, running_wheel

extension_data_loaders = {
    animal_gate.EXTENSION_NAME: animal_gate.io.import_data,
    consumption_scale.EXTENSION_NAME: consumption_scale.io.import_data,
    running_wheel.EXTENSION_NAME: running_wheel.io.import_data,
}


def import_intellimaze_dataset(path: Path) -> IntelliMazeDataset | None:
    """
    Import an IntelliMaze dataset from a zip file.

    This function extracts the zip file, imports metadata, devices, and animals,
    creates an IntelliMazeDataset, and loads data for each extension.

    Args:
        path (Path): The path to the zip file containing the IntelliMaze dataset.

    Returns:
        IntelliMazeDataset | None: The imported dataset, or None if the file is not a valid IntelliMaze dataset.
    """
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
                animals = _import_animals_v6(
                    tmp_path / "Animals" / "Animals.animals",
                    tmp_path / "Groups" / "Groups.groups",
                )
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

    # Extract factors from metadata
    factors: dict[str, Factor] = {}
    expected_factor_names = ("Group", "Sex", "Strain", "Treatment")
    for factor_name in expected_factor_names:
        factor = _extract_factor(factor_name, factors, dataset)
        if factor is not None:
            factors[factor.name] = factor

    if len(factors) > 0:
        dataset.set_factors(factors)

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _get_devices(metadata: dict) -> dict[str, list[str]]:
    """
    Extract device information from metadata.

    This function creates a dictionary mapping extension names to lists of device IDs.

    Args:
        metadata (dict): The metadata containing device information.

    Returns:
        dict[str, list[str]]: Dictionary mapping extension names to lists of device IDs.
    """
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
    """
    Import metadata from an XML file.

    This function reads an XML file and parses it into a dictionary.

    Args:
        path (Path): The path to the XML file.

    Returns:
        dict | None: The parsed metadata, or None if the file doesn't exist.
    """
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["ExperimentInfo"]


def _import_animals_v5(animals_file_path: Path) -> dict | None:
    """
    Import animal data from IntelliMaze version 5 format.

    This function reads an XML file containing animal data and creates a dictionary
    mapping animal IDs to Animal objects.

    Args:
        animals_file_path (Path): The path to the XML file containing animal data.

    Returns:
        dict | None: Dictionary mapping animal IDs to Animal objects, or None if the file doesn't exist.
    """
    if not animals_file_path.is_file():
        return None

    with open(animals_file_path, encoding="utf-8-sig") as file:
        animals_json = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    expected_fields = (
        "Sex",
        "Strain",
        "Group",
        "Treatment",
        "Dosage",
        "Notes",
    )

    present_fields = []
    # Check if a field is present in any of the animal
    for index, item in enumerate(animals_json["ArrayOfAnimal"]["Animal"]):
        for field in expected_fields:
            if field in item:
                present_fields.append(field)

    animals = {}
    for index, item in enumerate(animals_json["ArrayOfAnimal"]["Animal"]):
        properties = {
            "Tag": item["Tag"],
            "PMBoxNr": int(item["PMBoxNr"]),
            "Weight": float(item["Weight"]),
            "Age": int(item["Age"]),
        }
        # Add optional fields
        for field in present_fields:
            properties[field] = item[field] if field in item else ""

        animal = Animal(
            enabled=True,
            id=str(item["Name"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal
    return animals


def _import_animals_v6(animals_file_path: Path, groups_file_path: Path) -> dict | None:
    """
    Import animal data from IntelliMaze version 6.x format.

    This function reads XML files containing animal and group data and creates a dictionary
    mapping animal IDs to Animal objects. In version 6.x, groups are stored in a separate file.

    Args:
        animals_file_path (Path): The path to the XML file containing animal data.
        groups_file_path (Path): The path to the XML file containing group data.

    Returns:
        dict | None: Dictionary mapping animal IDs to Animal objects, or None if either file doesn't exist.
    """
    # Data format starting from IntelliMaze 6.x
    if not animals_file_path.is_file() or not groups_file_path.is_file():
        return None

    with open(animals_file_path, encoding="utf-8-sig") as file:
        animals_json = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    with open(groups_file_path, encoding="utf-8-sig") as file:
        groups_json = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    groups: dict[str, str] = {}
    # Map group id to group name
    for index, item in enumerate(groups_json["ArrayOfGroup"]["Group"]):
        groups[item["Id"]] = item["Name"]

    expected_fields = (
        "Sex",
        "Strain",
        "Treatment",
        "Dosage",
        "Notes",
    )

    present_fields = []
    # Check if a field is present in any of the animal
    for index, item in enumerate(animals_json["ArrayOfAnimal"]["Animal"]):
        for field in expected_fields:
            if field in item:
                present_fields.append(field)

    animals: dict[str, Animal] = {}
    for index, item in enumerate(animals_json["ArrayOfAnimal"]["Animal"]):
        properties = {
            "Tag": item["Tag"],
            "PMBoxNr": int(item["PMBoxNr"]),
            "Group": groups[item["GroupId"]],
            "Weight": float(item["Weight"]),
            "Age": int(item["Age"]),
        }
        # Add optional fields
        for field in present_fields:
            properties[field] = item[field] if field in item else ""

        animal = Animal(
            enabled=True,
            id=str(item["Name"]),
            color=get_color_hex(index),
            properties=properties,
        )
        animals[animal.id] = animal
    return animals


def _extract_factor(factor_name: str, factors: dict[str, Factor], dataset: IntelliMazeDataset) -> Factor | None:
    """
    Extract a factor from dataset properties.

    This function extracts levels for a factor from animal properties and creates a Factor object.

    Args:
        factor_name (str): The name of the factor to extract.
        factors (dict[str, Factor]): Dictionary of existing factors.
        dataset (IntelliMazeDataset): The dataset containing animal properties.

    Returns:
        Factor | None: The extracted factor, or None if no levels were found.
    """
    levels = dataset.extract_levels_from_property(factor_name)
    if len(levels) > 0:
        return Factor(factor_name, list(levels.values()))
    else:
        return None
