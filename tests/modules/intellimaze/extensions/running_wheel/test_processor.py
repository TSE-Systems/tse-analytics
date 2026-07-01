"""Tests for the IntelliMaze RunningWheel extension preprocessor.

``preprocess_data`` maps animal tags → ids, converts cumulative wheel counters to
per-interval differentials, and attaches a processed ``RunningWheel`` datatable.
"""

from unittest.mock import patch

import pandas as pd
import pytest
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellimaze.extensions.running_wheel.data.processor import (
    EXTENSION_NAME,
    preprocess_data,
)


@pytest.fixture
def dataset():
    animals = {
        "M1": Animal(id="M1", properties={"Tag": "T1"}),
        "M2": Animal(id="M2", properties={"Tag": "T2"}),
    }
    metadata = {
        "name": "IM",
        "animals": {},
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-01 01:00:00",
    }
    with patch("tse_analytics.core.data.dataset.messaging"):
        from tse_analytics.core.data.dataset import Dataset

        return Dataset("IM", "", "IntelliMaze", metadata, animals)


@pytest.fixture
def registration_data(dataset):
    """A raw RunningWheel 'Registration' table with cumulative Left/Right counters."""
    df = pd.DataFrame({
        "Time": pd.to_datetime([
            "2024-01-01 00:00",
            "2024-01-01 00:10",
            "2024-01-01 00:20",
            "2024-01-01 00:00",
            "2024-01-01 00:10",
        ]),
        "Tag": ["T1", "T1", "T1", "T2", "T2"],
        "DeviceId": ["D1", "D1", "D1", "D2", "D2"],
        "Left": [0, 5, 12, 0, 3],  # cumulative
        "Right": [0, 2, 5, 0, 1],
        "Reset": [0, 0, 0, 0, 0],
    })
    return {"Registration": Datatable(dataset, "Registration", "", {}, df, {})}


def test_preprocess_attaches_processed_datatable(dataset, registration_data):
    preprocess_data(dataset, registration_data)

    assert EXTENSION_NAME in dataset.datatables
    result = dataset.datatables[EXTENSION_NAME].df
    assert {"Animal", "DateTime", "Timedelta", "Left", "Right"} <= set(result.columns)
    # Raw device/tag columns are dropped after mapping.
    assert "Tag" not in result.columns
    assert "DeviceId" not in result.columns


def test_tags_are_mapped_to_animal_ids(dataset, registration_data):
    preprocess_data(dataset, registration_data)
    animals = set(dataset.datatables[EXTENSION_NAME].df["Animal"].astype("string"))
    assert animals == {"M1", "M2"}


def test_cumulative_counters_become_differentials(dataset, registration_data):
    preprocess_data(dataset, registration_data)
    result = dataset.datatables[EXTENSION_NAME].df

    m1 = result[result["Animal"] == "M1"].sort_values("DateTime")
    # Cumulative Left [0, 5, 12] -> differentials [0, 5, 7].
    assert m1["Left"].tolist() == [0, 5, 7]
    assert m1["Right"].tolist() == [0, 2, 3]
