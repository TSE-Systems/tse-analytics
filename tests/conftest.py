import sys
from unittest.mock import MagicMock

import pytest

# Mock resources_rc at module level so generated *_ui.py files
# (which use bare `import resources_rc`) can be imported during test collection.
sys.modules["resources_rc"] = MagicMock()


@pytest.fixture(scope="session")
def qapp():
    """A single QApplication instance shared by all Qt-dependent tests.

    Qt requires exactly one ``QApplication`` per process; the singleton guard
    lets this coexist with any app created elsewhere. Session-scoped so widget
    tests across modules reuse it instead of each defining their own copy.
    """
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def make_dataset():
    """Return a factory ``make_dataset(name="DS") -> Dataset``.

    Builds a fully-populated PhenoMaster ``Dataset`` — two animals, a custom
    ``Group`` factor, a ``Main`` datatable (nullable dtypes), and one report.
    Messaging is patched during construction so building test data never
    broadcasts on the global messenger.
    """
    from datetime import datetime
    from unittest.mock import patch

    import pandas as pd
    from tse_analytics.core.data.dataset import Dataset
    from tse_analytics.core.data.datatable import Datatable
    from tse_analytics.core.data.report import Report
    from tse_analytics.core.data.shared import (
        Aggregation,
        Animal,
        ByAnimalConfig,
        Factor,
        FactorLevel,
        FactorRole,
        Variable,
    )

    def _factory(name: str = "DS") -> Dataset:
        animals = {
            "A1": Animal(id="A1", properties={"group": "Control"}),
            "A2": Animal(id="A2", properties={"group": "Treatment"}),
        }
        metadata = {
            "name": name,
            "description": "",
            "experiment_started": "2024-01-01 00:00:00",
            "experiment_stopped": "2024-01-01 01:00:00",
            "animals": {aid: {"id": aid} for aid in animals},
        }
        with patch("tse_analytics.core.data.dataset.messaging"):
            dataset = Dataset(
                name=name,
                description="",
                dataset_type="PhenoMaster",
                metadata=metadata,
                animals=animals,
            )
        dataset.factors["Group"] = Factor(
            name="Group",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Control": FactorLevel(name="Control", color="#FF0000", animal_ids=["A1"]),
                "Treatment": FactorLevel(name="Treatment", color="#00FF00", animal_ids=["A2"]),
            },
        )

        df = pd.DataFrame({
            "Animal": pd.Categorical(["A1", "A2", "A1", "A2"]),
            "DateTime": pd.to_datetime(
                pd.Series([
                    "2024-01-01 00:00",
                    "2024-01-01 00:00",
                    "2024-01-01 01:00",
                    "2024-01-01 01:00",
                ])
            ),
            "Timedelta": pd.to_timedelta(["0h", "0h", "1h", "1h"]),
            "Weight": pd.array([25.0, 26.0, 25.5, 26.5], dtype="Float64"),
        })
        variables = {
            "Weight": Variable(
                name="Weight",
                unit="g",
                description="Body weight",
                type="float",
                aggregation=Aggregation.MEAN,
                remove_outliers=False,
            )
        }
        datatable = Datatable(dataset, "Main", "Main datatable", variables, df, {})
        dataset.datatables["Main"] = datatable
        dataset.reports["R1"] = Report(dataset, "R1", "<p>report</p>", datetime(2024, 1, 1, 12, 0, 0))
        return dataset

    return _factory
