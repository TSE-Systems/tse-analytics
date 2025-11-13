"""
IntelliCage Dataset Loader Module.

This module provides functions for loading IntelliCage datasets from zip files.
It detects the version of the IntelliCage data format and delegates to the
appropriate version-specific loader.
"""

import tempfile
import timeit
import zipfile
from pathlib import Path
from typing import Protocol

import xmltodict
from loguru import logger

from tse_analytics.core.data.shared import Factor
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset
from tse_analytics.modules.intellicage.io.dataset_loader_v1 import import_intellicage_dataset_v1
from tse_analytics.modules.intellicage.io.dataset_loader_v2 import import_intellicage_dataset_v2


class IntelliCageDatasetLoader(Protocol):
    """Protocol for dataset loader functions."""

    def __call__(self, path: Path, tmp_path: Path, data_descriptor: dict) -> IntelliCageDataset | None: ...


def import_intellicage_dataset(path: Path) -> IntelliCageDataset | None:
    """
    Import an IntelliCage dataset from a zip file.

    This function extracts the contents of the zip file to a temporary directory,
    determines the version of the IntelliCage data format, and delegates to the
    appropriate version-specific loader. It also extracts factors from the metadata.

    Parameters
    ----------
    path : Path
        Path to the IntelliCage dataset zip file.

    Returns
    -------
    IntelliCageDataset | None
        The imported dataset, or None if the import failed.
    """
    tic = timeit.default_timer()

    dataset_loaders: dict[str, IntelliCageDatasetLoader] = {
        "OldDataFormat": import_intellicage_dataset_v1,  # Data from Angel
        "Prototype1": import_intellicage_dataset_v1,  # Prototype version 1 of the new data structure
        "Prototype2": import_intellicage_dataset_v1,  # Prototype version 2 of the new data structure
        "Version1": import_intellicage_dataset_v1,  # Version 1 of the new data structure
        "Version_2_2": import_intellicage_dataset_v2,  # Data structure of the release 2.2
        "IntelliCage_Plus_2_2_2": import_intellicage_dataset_v2,  # Data structure of the IntelliCage Plus 2.2.2
        "IntelliCage_Plus_2_3": import_intellicage_dataset_v2,  # IntelliCage Plus 2.3
        "IntelliCage_Plus_3": import_intellicage_dataset_v2,  # IntelliCage Plus 2.3.1+
        "IntelliCage_Plus_3_1": import_intellicage_dataset_v2,  # IntelliCage Plus 3.1.x+
        "IntelliCage_Plus_3_3_8": import_intellicage_dataset_v2,  # IntelliCage Plus 3.3.8+
        "IntelliCage_Plus_3_6_0": import_intellicage_dataset_v2,  # IntelliCage Plus 3.6.0+ (ActivityBox data format)
        "IntelliCage_Plus_3_6_4": import_intellicage_dataset_v2,  # IntelliCage Plus 3.6.4 (TTL data added)
        "IntelliCage_Plus_3_6_5": import_intellicage_dataset_v2,  # IntelliCage Plus 3.6.5 (MqttSocialBox data added)
    }

    with zipfile.ZipFile(path, mode="r") as zip:
        with tempfile.TemporaryDirectory(prefix="tse-analytics-") as tempdir:
            tmp_path = Path(tempdir)
            zip.extractall(tempdir)

            data_descriptor = _import_data_descriptor(tmp_path / "DataDescriptor.xml")
            loader = dataset_loaders.get(data_descriptor["Version"], import_intellicage_dataset_v2)
            dataset = loader(path, tmp_path, data_descriptor)

    # Extract factors from metadata
    factors: dict[str, Factor] = {}
    expected_factor_names = ("Sex", "Group")
    for factor_name in expected_factor_names:
        factor = _extract_factor(factor_name, factors, dataset)
        if factor is not None:
            factors[factor.name] = factor

    if len(factors) > 0:
        dataset.set_factors(factors)

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _import_data_descriptor(path: Path) -> dict | None:
    """
    Import the data descriptor XML file.

    This function reads and parses the DataDescriptor.xml file, which contains
    metadata about the IntelliCage experiment.

    Parameters
    ----------
    path : Path
        Path to the DataDescriptor.xml file.

    Returns
    -------
    dict | None
        Dictionary containing the parsed data descriptor, or None if the file
        does not exist or could not be parsed.
    """
    if not path.is_file():
        return None

    with open(path, encoding="utf-8-sig") as file:
        result = xmltodict.parse(
            file.read(),
            process_namespaces=False,
            xml_attribs=False,
        )

    return result["DataDescriptor"]


def _extract_factor(factor_name: str, factors: dict[str, Factor], dataset: IntelliCageDataset) -> Factor | None:
    """
    Extract a factor from the dataset's animal properties.

    This function extracts a factor (e.g., Sex, Group) from the animal properties
    in the dataset and creates a Factor object with the unique levels found.

    Parameters
    ----------
    factor_name : str
        Name of the factor to extract (e.g., "Sex", "Group").
    factors : dict[str, Factor]
        Dictionary of existing factors.
    dataset : IntelliCageDataset
        The dataset from which to extract the factor.

    Returns
    -------
    Factor | None
        A Factor object with the extracted levels, or None if no levels were found.
    """
    levels = dataset.extract_levels_from_property(factor_name)
    if len(levels) > 0:
        return Factor(factor_name, list(levels.values()))
    else:
        return None
