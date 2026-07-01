"""Regression tests for the DrinkFeed interval processor (Datatable generation)."""

from datetime import time
from unittest.mock import patch

import pandas as pd
import pytest


@pytest.fixture
def drinkfeed_input_datatable():
    """A minimal PhenoMaster-style bin datatable usable as DrinkFeed processor input."""
    from tse_analytics.core.data.dataset import Dataset
    from tse_analytics.core.data.datatable import Datatable
    from tse_analytics.core.data.shared import Aggregation, Animal, Variable

    animals = {
        "A1": Animal(id="A1", properties={"group": "Control"}),
        "A2": Animal(id="A2", properties={"group": "Treatment"}),
    }
    metadata = {
        "name": "DS",
        "description": "",
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-01 04:00:00",
        "animals": {aid: {"id": aid} for aid in animals},
    }
    with patch("tse_analytics.core.data.dataset.messaging"):
        dataset = Dataset(
            name="DS",
            description="",
            dataset_type="PhenoMaster",
            metadata=metadata,
            animals=animals,
        )

    base = pd.Timestamp("2024-01-01 00:00:00")
    interval = pd.Timedelta("1h")
    rows = []
    for i in range(4):
        for animal in ("A1", "A2"):
            rows.append({
                "Animal": animal,
                "DateTime": base + i * interval,
                "Timedelta": i * interval,
                "Drink": 1.0 + i,
            })
    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Timedelta"] = pd.to_timedelta(df["Timedelta"])
    df["Drink"] = df["Drink"].astype("Float64")

    variables = {
        "Drink": Variable("Drink", "ml", "Drink amount", "Float64", Aggregation.SUM, False),
    }
    datatable = Datatable(dataset, "DrinkFeedBin", "Raw bin", variables, df, {"sample_interval": interval})
    dataset.datatables["DrinkFeedBin"] = datatable
    return datatable


def test_intervals_result_is_regular_timeseries(drinkfeed_input_datatable):
    """Regression: the generated intervals datatable must be a regular time series.

    The sample interval used to be stored under a misspelled metadata key
    (``"samping_interval"``), so ``is_regular_timeseries`` was wrongly ``False``. The interval
    processor now passes ``sample_interval=`` to ``Datatable.from_dataframe``.
    """
    from tse_analytics.modules.phenomaster.extensions.drinkfeed.drinkfeed_settings import DrinkFeedSettings
    from tse_analytics.modules.phenomaster.extensions.drinkfeed.interval_processor import process_drinkfeed_intervals

    settings = DrinkFeedSettings(
        sequential_analysis_type=False,
        intermeal_interval=time(minute=5),
        drinking_minimum_amount=0.05,
        feeding_minimum_amount=0.05,
        fixed_interval=time(hour=1),
        diets=[],
    )
    result = process_drinkfeed_intervals(drinkfeed_input_datatable, settings, {})

    assert result.is_regular_timeseries is True
    assert result.sample_interval == pd.Timedelta("1h")
