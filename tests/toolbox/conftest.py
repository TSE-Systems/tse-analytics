"""
Shared pytest fixtures for toolbox processor tests.

Provides DataFrames and Dataset instances suitable for statistical analyses
that the toolbox processors perform.
"""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    Factor,
    FactorLevel,
    Variable,
)


@pytest.fixture
def analysis_animals():
    """6 animals, all enabled, split into 2 groups."""
    animals = {}
    for i in range(1, 7):
        group = "Control" if i <= 3 else "Treatment"
        animals[f"M{i}"] = Animal(
            enabled=True,
            id=f"M{i}",
            color=f"#{'FF' if i <= 3 else '00'}0000",
            properties={"group": group},
        )
    return animals


@pytest.fixture
def analysis_variables():
    """Two numeric variables for analysis."""
    return {
        "Metabolism": Variable(
            name="Metabolism",
            unit="kcal/h",
            description="Metabolic rate",
            type="float",
            aggregation=Aggregation.MEAN,
            remove_outliers=False,
        ),
        "Activity": Variable(
            name="Activity",
            unit="counts",
            description="Activity counts",
            type="float",
            aggregation=Aggregation.SUM,
            remove_outliers=False,
        ),
    }


@pytest.fixture
def analysis_factor():
    """Factor with Control and Treatment levels."""
    return Factor(
        name="Group",
        levels=[
            FactorLevel(name="Control", color="#FF0000", animal_ids=["M1", "M2", "M3"]),
            FactorLevel(name="Treatment", color="#00FF00", animal_ids=["M4", "M5", "M6"]),
        ],
    )


@pytest.fixture
def analysis_df(analysis_animals, analysis_factor):
    """DataFrame with 6 animals × 24 timepoints = 144 rows.
    Control group has lower Metabolism, Treatment has higher.
    """
    rng = np.random.default_rng(42)
    base_time = pd.Timestamp("2024-01-01")
    interval = pd.Timedelta("1h")

    rows = []
    for i in range(24):
        for animal_id, animal in analysis_animals.items():
            group = animal.properties["group"]
            base_metabolism = 5.0 if group == "Control" else 8.0
            base_activity = 100.0 if group == "Control" else 150.0

            rows.append({
                "Animal": animal_id,
                "DateTime": base_time + i * interval,
                "Timedelta": i * interval,
                "Bin": i,
                "Metabolism": base_metabolism + rng.normal(0, 0.5),
                "Activity": base_activity + rng.normal(0, 10),
                "Group": group,
            })

    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Timedelta"] = pd.to_timedelta(df["Timedelta"])
    df["Group"] = df["Group"].astype("category")
    df["Run"] = pd.Categorical([1] * len(df))
    return df


@pytest.fixture
def analysis_dataset(analysis_animals, analysis_factor, analysis_variables, analysis_df):
    """Fully configured Dataset with factors and a datatable."""
    metadata = {
        "name": "Analysis Dataset",
        "description": "Test dataset for analysis",
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-02 00:00:00",
        "animals": {aid: {"id": aid} for aid in analysis_animals},
    }

    with patch("tse_analytics.core.data.dataset.messaging"):
        dataset = Dataset(metadata=metadata, animals=analysis_animals)
        dataset.factors = {"Group": analysis_factor}

        datatable = Datatable(
            dataset=dataset,
            name="Main",
            description="Main datatable",
            variables=analysis_variables,
            df=analysis_df,
            sampling_interval=pd.Timedelta("1h"),
        )
        dataset.datatables["Main"] = datatable

    return dataset
