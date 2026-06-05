"""Faithful repro: grouping via the real set_factors path."""

import os
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import time

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    ByAnimalPropertyConfig,
    ByTimeOfDayConfig,
    Factor,
    FactorLevel,
    FactorRole,
    Variable,
)
from tse_analytics.toolbox.composite_score.processor import get_composite_score_result

app = QApplication([])

animals = {
    f"M{i}": Animal(id=f"M{i}", properties={"Genotype": "WT" if i <= 3 else "KO"}) for i in range(1, 7)
}
variables = {
    "Metabolism": Variable("Metabolism", "kcal/h", "Metabolic rate", "float", Aggregation.MEAN, False),
    "Activity": Variable("Activity", "counts", "Activity counts", "float", Aggregation.SUM, False),
}

rng = np.random.default_rng(1)
rows = []
for i in range(24):
    for aid, animal in animals.items():
        wt = animal.properties["Genotype"] == "WT"
        rows.append({
            "Animal": aid,
            "DateTime": pd.Timestamp("2024-01-01") + i * pd.Timedelta("1h"),
            "Timedelta": i * pd.Timedelta("1h"),
            "Metabolism": (5.0 if wt else 8.0) + rng.normal(0, 0.5),
            "Activity": (100.0 if wt else 150.0) + rng.normal(0, 10),
        })
df = pd.DataFrame(rows)
df["Animal"] = df["Animal"].astype("category")

with patch("tse_analytics.core.data.dataset.messaging"):
    dataset = Dataset(
        name="Repro",
        description="",
        dataset_type="PhenoMaster",
        metadata={"name": "Repro", "animals": {aid: {"id": aid} for aid in animals}},
        animals=animals,
    )
    datatable = Datatable(dataset=dataset, name="Main", description="", variables=variables, df=df, metadata={})
    dataset.datatables["Main"] = datatable

    # Materialize factor columns the real way.
    genotype = Factor(
        name="Genotype",
        config=ByAnimalPropertyConfig(property_key="Genotype"),
        role=FactorRole.BETWEEN_SUBJECT,
        levels={
            "WT": FactorLevel(name="WT", color="#FF0000"),
            "KO": FactorLevel(name="KO", color="#00FF00"),
        },
    )
    light = Factor(
        name="LightCycle",
        config=ByTimeOfDayConfig(light_cycle_start=time(7, 0), dark_cycle_start=time(19, 0)),
        role=FactorRole.WITHIN_SUBJECT,
        levels={"Light": FactorLevel(name="Light", color="#111111"), "Dark": FactorLevel(name="Dark", color="#222222")},
    )
    dataset.factors = {"Genotype": genotype, "LightCycle": light}
    datatable.set_factors(dataset.factors)

print("df columns after set_factors:", list(datatable.df.columns))
print("Genotype in df:", "Genotype" in datatable.df.columns, "| LightCycle in df:", "LightCycle" in datatable.df.columns)

dirs = {"Metabolism": "higher", "Activity": "higher"}
wts = {"Metabolism": 1.0, "Activity": 1.0}

for fname in ["Genotype", "LightCycle"]:
    print("\n===== group_by =", fname, "=====")
    res = get_composite_score_result(datatable, ["Metabolism", "Activity"], dirs, wts, "zscore", fname)
    if res is None:
        print("  RESULT IS None")
        continue
    print(res.scores_df.to_string())
    print("  has 'Group summary' in report:", "Group summary" in res.report)
