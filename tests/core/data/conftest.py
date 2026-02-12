"""
Shared pytest fixtures for core/data/ tests.

Provides reusable DataFrames, Animals, Variables, Datasets, and Datatables
to minimize boilerplate across test modules.

Imports of Dataset/Datatable are done inside fixtures to avoid
circular import issues (dataset → messaging → messages → dataset).
"""

from unittest.mock import patch

import pandas as pd
import pytest
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    Factor,
    FactorLevel,
    Variable,
)


@pytest.fixture
def sample_animals():
    """3 animals: A1 and A2 enabled, A3 disabled."""
    return {
        "A1": Animal(enabled=True, id="A1", color="#FF0000", properties={"group": "Control"}),
        "A2": Animal(enabled=True, id="A2", color="#00FF00", properties={"group": "Treatment"}),
        "A3": Animal(enabled=False, id="A3", color="#0000FF", properties={"group": "Treatment"}),
    }


@pytest.fixture
def sample_variables():
    """Two numeric variables: Weight (mean, outlier removal) and Speed (sum, no outlier removal)."""
    return {
        "Weight": Variable(
            name="Weight",
            unit="g",
            description="Body weight",
            type="float",
            aggregation=Aggregation.MEAN,
            remove_outliers=True,
        ),
        "Speed": Variable(
            name="Speed",
            unit="m/s",
            description="Movement speed",
            type="float",
            aggregation=Aggregation.SUM,
            remove_outliers=False,
        ),
    }


@pytest.fixture
def sample_factor():
    """Factor with 2 levels: Control (A1) and Treatment (A2, A3)."""
    return Factor(
        name="Group",
        levels=[
            FactorLevel(name="Control", color="#FF0000", animal_ids=["A1"]),
            FactorLevel(name="Treatment", color="#00FF00", animal_ids=["A2", "A3"]),
        ],
    )


@pytest.fixture
def sample_df():
    """Small DataFrame: 3 animals × 5 timepoints = 15 rows."""
    base_time = pd.Timestamp("2024-01-01 00:00:00")
    interval = pd.Timedelta("1h")

    rows = []
    for i in range(5):
        for animal in ["A1", "A2", "A3"]:
            rows.append({
                "Animal": animal,
                "DateTime": base_time + i * interval,
                "Timedelta": i * interval,
                "Bin": i,
                "Weight": 25.0 + i * 0.5 + (hash(animal) % 3),
                "Speed": 1.0 + i * 0.1 + (hash(animal) % 2) * 0.5,
            })

    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Timedelta"] = pd.to_timedelta(df["Timedelta"])
    return df


@pytest.fixture
def sample_metadata():
    """Minimal dataset metadata dict."""
    return {
        "name": "Test Dataset",
        "description": "A test dataset",
        "source_path": "/test/path",
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-01 05:00:00",
        "animals": {
            "A1": {"id": "A1", "group": "Control"},
            "A2": {"id": "A2", "group": "Treatment"},
            "A3": {"id": "A3", "group": "Treatment"},
        },
    }


@pytest.fixture
def sample_dataset(sample_animals, sample_metadata):
    """A Dataset instance with sample animals and metadata."""
    from tse_analytics.core.data.dataset import Dataset

    with patch("tse_analytics.core.data.dataset.messaging"):
        dataset = Dataset(metadata=sample_metadata, animals=sample_animals)
    return dataset


@pytest.fixture
def sample_datatable(sample_dataset, sample_variables, sample_df):
    """A Datatable attached to sample_dataset."""
    from tse_analytics.core.data.datatable import Datatable

    datatable = Datatable(
        dataset=sample_dataset,
        name="Main",
        description="Main datatable",
        variables=sample_variables,
        df=sample_df,
        sampling_interval=pd.Timedelta("1h"),
    )
    sample_dataset.datatables["Main"] = datatable
    return datatable
