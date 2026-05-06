"""Tests for the factor applier dispatch in tse_analytics.core.data.factor_appliers.

Imports of ``Dataset`` are avoided to side-step a pre-existing circular-import
issue between ``dataset`` / ``datatable`` / ``messaging``. Each applier only
reads ``dataset.animals`` (and only ``_apply_by_animal_property`` actually
uses it), so a small duck-typed stub suffices.
"""

from datetime import time, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest
from tse_analytics.core.data.factor_appliers import (
    FACTOR_APPLIERS,
    _apply_by_animal,
    _apply_by_animal_property,
    _apply_by_column,
    _apply_by_elapsed_time,
    _apply_by_time_interval,
    _apply_by_time_of_day,
)
from tse_analytics.core.data.shared import (
    Animal,
    ByAnimalConfig,
    ByAnimalPropertyConfig,
    ByColumnConfig,
    ByElapsedTimeConfig,
    ByTimeIntervalConfig,
    ByTimeOfDayConfig,
    Factor,
    FactorLevel,
    FactorRole,
    TimePhase,
)


@pytest.fixture
def stub_dataset():
    """Duck-typed dataset with the only attribute appliers read: ``animals``."""
    animals = {
        "A1": Animal(id="A1", properties={"Genotype": "WT", "Sex": "F"}),
        "A2": Animal(id="A2", properties={"Genotype": "KO", "Sex": "F"}),
        "A3": Animal(id="A3", properties={"Genotype": "KO", "Sex": "M"}),
    }
    return SimpleNamespace(animals=animals)


@pytest.fixture
def time_df():
    """Three animals across four hours, with DateTime + Timedelta columns."""
    base = pd.Timestamp("2024-01-01 06:00:00")
    rows = []
    for i in range(4):
        for animal in ["A1", "A2", "A3"]:
            rows.append({
                "Animal": animal,
                "DateTime": base + pd.Timedelta(hours=i),
                "Timedelta": pd.Timedelta(hours=i),
            })
    return pd.DataFrame(rows)


class TestDispatchRegistry:
    """The registry must enumerate one applier per FactorConfig type."""

    def test_registry_covers_all_config_types(self):
        assert set(FACTOR_APPLIERS) == {
            ByAnimalConfig,
            ByAnimalPropertyConfig,
            ByTimeOfDayConfig,
            ByElapsedTimeConfig,
            ByColumnConfig,
            ByTimeIntervalConfig,
        }

    def test_registry_maps_to_expected_functions(self):
        assert FACTOR_APPLIERS[ByAnimalConfig] is _apply_by_animal
        assert FACTOR_APPLIERS[ByAnimalPropertyConfig] is _apply_by_animal_property
        assert FACTOR_APPLIERS[ByTimeOfDayConfig] is _apply_by_time_of_day
        assert FACTOR_APPLIERS[ByElapsedTimeConfig] is _apply_by_elapsed_time
        assert FACTOR_APPLIERS[ByColumnConfig] is _apply_by_column
        assert FACTOR_APPLIERS[ByTimeIntervalConfig] is _apply_by_time_interval


class TestByAnimalApplier:
    def test_assigns_levels_per_animal(self, time_df, stub_dataset):
        factor = Factor(
            name="Group",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Ctrl": FactorLevel(name="Ctrl", color="#000", animal_ids=["A1"]),
                "Trt": FactorLevel(name="Trt", color="#000", animal_ids=["A2", "A3"]),
            },
        )
        _apply_by_animal(time_df, factor, stub_dataset)

        assert "Group" in time_df.columns
        assert time_df.loc[time_df["Animal"] == "A1", "Group"].unique().tolist() == ["Ctrl"]
        assert set(time_df.loc[time_df["Animal"] == "A2", "Group"].unique()) == {"Trt"}

    def test_unassigned_animals_get_na(self, time_df, stub_dataset):
        factor = Factor(
            name="Partial",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={"Only": FactorLevel(name="Only", color="#000", animal_ids=["A1"])},
        )
        _apply_by_animal(time_df, factor, stub_dataset)

        a3_values = time_df.loc[time_df["Animal"] == "A3", "Partial"]
        assert a3_values.isna().all()


class TestByAnimalPropertyApplier:
    def test_derives_levels_from_animal_property(self, time_df, stub_dataset):
        factor = Factor(
            name="Genotype",
            role=FactorRole.BETWEEN_SUBJECT,
            config=ByAnimalPropertyConfig(property_key="Genotype"),
        )
        _apply_by_animal_property(time_df, factor, stub_dataset)

        assert "Genotype" in time_df.columns
        assert time_df.loc[time_df["Animal"] == "A1", "Genotype"].unique().tolist() == ["WT"]
        assert set(time_df.loc[time_df["Animal"].isin(["A2", "A3"]), "Genotype"]) == {"KO"}

    def test_missing_property_yields_na(self, time_df, stub_dataset):
        # Drop the Sex property from A1 to test fallback
        stub_dataset.animals["A1"] = Animal(id="A1", properties={"Genotype": "WT"})
        factor = Factor(
            name="Sex",
            role=FactorRole.BETWEEN_SUBJECT,
            config=ByAnimalPropertyConfig(property_key="Sex"),
        )
        _apply_by_animal_property(time_df, factor, stub_dataset)

        a1_values = time_df.loc[time_df["Animal"] == "A1", "Sex"]
        assert a1_values.isna().all()


class TestByTimeOfDayApplier:
    def test_assigns_light_dark_by_hour(self, time_df, stub_dataset):
        factor = Factor(
            name="LightCycle",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeOfDayConfig(
                light_cycle_start=time(7, 0),
                dark_cycle_start=time(19, 0),
            ),
        )
        _apply_by_time_of_day(time_df, factor, stub_dataset)

        # 06:00 → Dark, 07:00–08:00 → Light
        assert time_df.loc[time_df["DateTime"].dt.hour == 6, "LightCycle"].unique().tolist() == ["Dark"]
        assert time_df.loc[time_df["DateTime"].dt.hour == 7, "LightCycle"].unique().tolist() == ["Light"]

    def test_skips_when_datetime_column_missing(self, stub_dataset):
        df = pd.DataFrame({"Animal": ["A1", "A2"]})
        factor = Factor(
            name="LC",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeOfDayConfig(
                light_cycle_start=time(7, 0),
                dark_cycle_start=time(19, 0),
            ),
        )
        _apply_by_time_of_day(df, factor, stub_dataset)
        assert "LC" not in df.columns


class TestByElapsedTimeApplier:
    def test_assigns_phases_by_elapsed_time(self, time_df, stub_dataset):
        factor = Factor(
            name="Phase",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByElapsedTimeConfig(
                phases=[
                    TimePhase(name="Early", start_timestamp=timedelta(0)),
                    TimePhase(name="Late", start_timestamp=timedelta(hours=2)),
                ],
            ),
        )
        _apply_by_elapsed_time(time_df, factor, stub_dataset)

        early = time_df.loc[time_df["Timedelta"] < pd.Timedelta(hours=2), "Phase"].unique().tolist()
        late = time_df.loc[time_df["Timedelta"] >= pd.Timedelta(hours=2), "Phase"].unique().tolist()
        assert early == ["Early"]
        assert late == ["Late"]

    def test_skips_when_no_phases(self, time_df, stub_dataset):
        factor = Factor(
            name="Phase",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByElapsedTimeConfig(phases=[]),
        )
        _apply_by_elapsed_time(time_df, factor, stub_dataset)
        assert "Phase" not in time_df.columns


class TestByColumnApplier:
    def test_aliases_existing_column(self, time_df, stub_dataset):
        time_df["Cohort"] = "C1"
        factor = Factor(
            name="CohortFactor",
            role=FactorRole.BETWEEN_SUBJECT,
            config=ByColumnConfig(column="Cohort"),
        )
        _apply_by_column(time_df, factor, stub_dataset)

        assert "CohortFactor" in time_df.columns
        assert time_df["CohortFactor"].dtype.name == "category"
        assert time_df["CohortFactor"].unique().tolist() == ["C1"]

    def test_skips_when_column_missing(self, time_df, stub_dataset):
        factor = Factor(
            name="Missing",
            role=FactorRole.BETWEEN_SUBJECT,
            config=ByColumnConfig(column="DoesNotExist"),
        )
        _apply_by_column(time_df, factor, stub_dataset)
        assert "Missing" not in time_df.columns


class TestByTimeIntervalApplier:
    def test_assigns_categorical_bins(self, time_df, stub_dataset):
        factor = Factor(
            name="Hour",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(hours=1)),
            levels={f"Hour {i}": FactorLevel(name=f"Hour {i}", color="#000000") for i in range(4)},
        )
        _apply_by_time_interval(time_df, factor, stub_dataset)

        assert "Hour" in time_df.columns
        assert time_df["Hour"].dtype.name == "category"
        assert time_df["Hour"].cat.ordered
        # 4 hourly timepoints map to "Hour 0".."Hour 3"
        assert set(time_df["Hour"].unique().tolist()) == {"Hour 0", "Hour 1", "Hour 2", "Hour 3"}

    def test_collapses_to_zero_with_24h_interval(self, time_df, stub_dataset):
        factor = Factor(
            name="Day",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(days=1)),
            levels={"Day 0": FactorLevel(name="Day 0", color="#000000")},
        )
        _apply_by_time_interval(time_df, factor, stub_dataset)

        assert (time_df["Day"] == "Day 0").all()

    def test_skips_when_timedelta_missing(self, stub_dataset):
        df = pd.DataFrame({"Animal": ["A1", "A2"]})
        factor = Factor(
            name="Hour",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(hours=1)),
            levels={"Hour 0": FactorLevel(name="Hour 0", color="#000000")},
        )
        _apply_by_time_interval(df, factor, stub_dataset)
        assert "Hour" not in df.columns

    def test_skips_when_interval_non_positive(self, time_df, stub_dataset):
        factor = Factor(
            name="Bad",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByTimeIntervalConfig(interval=timedelta(0)),
            levels={"Hour 0": FactorLevel(name="Hour 0", color="#000000")},
        )
        _apply_by_time_interval(time_df, factor, stub_dataset)
        assert "Bad" not in time_df.columns
