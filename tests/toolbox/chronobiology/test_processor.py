"""Tests for tse_analytics.toolbox.chronobiology.processor."""

import re
from datetime import time
from unittest.mock import patch

import matplotlib
import numpy as np
import pandas as pd
import pytest
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    ByAnimalConfig,
    Factor,
    FactorLevel,
    FactorRole,
    Variable,
)
from tse_analytics.toolbox.chronobiology.processor import (
    ChronobiologyResult,
    _compute_zeitgeber_time,
    _detect_onset_offset,
    _fit_cosinor,
    _fit_two_component_cosinor,
    _lombscargle_period,
    get_chronobiology_result,
)

matplotlib.use("Agg")


# ---------------------------------------------------------------------------
# Pure-function tests (no Qt / Datatable needed)
# ---------------------------------------------------------------------------


class TestFitCosinor:
    def test_recovers_known_parameters(self):
        t = np.arange(0, 240, 1.0)
        mesor, amplitude, acrophase, period = 10.0, 5.0, 8.0, 24.0
        omega = 2 * np.pi / period
        y = mesor + amplitude * np.cos(omega * (t - acrophase))

        fit = _fit_cosinor(t, y, period)

        assert fit["MESOR"] == pytest.approx(mesor, abs=1e-6)
        assert fit["Amplitude"] == pytest.approx(amplitude, abs=1e-6)
        assert fit["Acrophase_h"] == pytest.approx(acrophase, abs=1e-6)
        assert fit["PR"] == pytest.approx(1.0, abs=1e-9)
        assert fit["p_value"] < 1e-6

    def test_constant_series_is_degenerate(self):
        t = np.arange(0, 48, 1.0)
        y = np.full_like(t, 3.0)
        fit = _fit_cosinor(t, y, 24.0)
        assert np.isnan(fit["MESOR"])
        assert np.isnan(fit["Amplitude"])

    def test_too_few_points(self):
        fit = _fit_cosinor(np.array([0.0, 1.0]), np.array([1.0, 2.0]), 24.0)
        assert np.isnan(fit["MESOR"])
        assert fit["N"] == 2.0


class TestFitTwoComponentCosinor:
    def test_recovers_two_components(self):
        t = np.arange(0, 240, 1.0)
        m, a1, a2, p1, p2, phi1, phi2 = 10.0, 5.0, 2.0, 24.0, 12.0, 8.0, 3.0
        y = m + a1 * np.cos(2 * np.pi / p1 * (t - phi1)) + a2 * np.cos(2 * np.pi / p2 * (t - phi2))
        fit = _fit_two_component_cosinor(t, y, p1, p2)
        assert fit["MESOR"] == pytest.approx(m, abs=1e-6)
        assert fit["Amplitude_1"] == pytest.approx(a1, abs=1e-6)
        assert fit["Amplitude_2"] == pytest.approx(a2, abs=1e-6)
        assert fit["Acrophase_1_h"] == pytest.approx(phi1, abs=1e-6)
        assert fit["Acrophase_2_h"] == pytest.approx(phi2, abs=1e-6)

    def test_equal_periods_returns_nan(self):
        t = np.arange(0, 240, 1.0)
        y = 10.0 + np.cos(2 * np.pi / 24.0 * t)
        fit = _fit_two_component_cosinor(t, y, 24.0, 24.0)
        assert np.isnan(fit["MESOR"])


class TestLombScarglePeriod:
    def test_detects_injected_period(self):
        rng = np.random.default_rng(0)
        t = np.arange(0, 240, 0.5)
        y = np.cos(2 * np.pi / 24.0 * t) + rng.normal(0, 0.05, t.size)
        period, power, dominant = _lombscargle_period(t, y)
        assert period.size > 0
        assert power.size == period.size
        assert dominant == pytest.approx(24.0, abs=1.0)

    def test_constant_series_returns_empty(self):
        t = np.arange(0, 48, 1.0)
        y = np.ones_like(t)
        period, power, dominant = _lombscargle_period(t, y)
        assert period.size == 0
        assert power.size == 0
        assert np.isnan(dominant)


class TestZeitgeberTime:
    def test_zt_zero_at_lights_on(self):
        dt = pd.Series(pd.to_datetime(["2024-01-01 07:00", "2024-01-01 19:00", "2024-01-01 06:00"]))
        zt = _compute_zeitgeber_time(dt, time(7, 0))
        assert zt.iloc[0] == pytest.approx(0.0)
        assert zt.iloc[1] == pytest.approx(12.0)
        assert zt.iloc[2] == pytest.approx(23.0)


class TestDetectOnsetOffset:
    def test_midnight_spanning_block_not_split(self):
        # Nocturnal block active during the dark phase (19:00 -> 07:00).
        # The circadian day starts at lights-on (07:00), so the block stays
        # contiguous within a single circadian day rather than being split.
        dt = pd.date_range("2024-01-01 07:00", "2024-01-04 06:00", freq="1h")
        hours = dt.hour
        activity = np.where((hours >= 19) | (hours < 7), 10.0, 0.0)
        df = pd.DataFrame({"DateTime": dt, "Activity": activity})

        result = _detect_onset_offset(df, "Activity", 50.0, time(7, 0))

        assert len(result) == 3  # three complete circadian days
        for _, row in result.iterrows():
            assert row["Onset (ZT)"] == pytest.approx(12.0)  # 19:00
            assert row["Offset (ZT)"] == pytest.approx(23.0)  # 06:00
            assert row["Alpha_h"] == pytest.approx(11.0)


# ---------------------------------------------------------------------------
# Report-level tests (synthetic Datatable)
# ---------------------------------------------------------------------------


@pytest.fixture
def chrono_animals():
    """6 animals split into 2 groups of 3."""
    animals = {}
    for i in range(1, 7):
        group = "Control" if i <= 3 else "Treatment"
        animals[f"M{i}"] = Animal(id=f"M{i}", properties={"group": group})
    return animals


@pytest.fixture
def chrono_group_factor():
    return Factor(
        name="Group",
        config=ByAnimalConfig(),
        role=FactorRole.BETWEEN_SUBJECT,
        levels={
            "Control": FactorLevel(name="Control", color="#FF0000", animal_ids=["M1", "M2", "M3"]),
            "Treatment": FactorLevel(name="Treatment", color="#00FF00", animal_ids=["M4", "M5", "M6"]),
        },
    )


@pytest.fixture
def chrono_df(chrono_animals):
    """6 animals × 72 hourly timepoints (3 days) with a circadian signal."""
    rng = np.random.default_rng(42)
    base_time = pd.Timestamp("2024-01-01 00:00:00")
    interval = pd.Timedelta("1h")
    n_points = 72  # 3 days

    rows = []
    for i in range(n_points):
        dt = base_time + i * interval
        hour = dt.hour
        for animal_id, animal in chrono_animals.items():
            offset = 0.0 if animal.properties["group"] == "Control" else 10.0
            activity = 50.0 + offset + 20.0 * np.cos(2 * np.pi / 24.0 * (hour - 2)) + rng.normal(0, 1.0)
            rows.append({
                "Animal": animal_id,
                "DateTime": dt,
                "Timedelta": i * interval,
                "Activity": activity,
                "Group": animal.properties["group"],
                "Total": "All animals",
            })

    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Timedelta"] = pd.to_timedelta(df["Timedelta"])
    df["Group"] = df["Group"].astype("category")
    df["Total"] = df["Total"].astype("category")
    df["Activity"] = df["Activity"].astype("Float64")
    return df


@pytest.fixture
def chrono_variable():
    return {
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
def chrono_dataset(chrono_animals, chrono_group_factor, chrono_variable, chrono_df):
    metadata = {
        "name": "Chrono Dataset",
        "description": "Chronobiology test dataset",
        "experiment_started": "2024-01-01 00:00:00",
        "experiment_stopped": "2024-01-04 00:00:00",
    }
    with patch("tse_analytics.core.data.dataset.messaging"):
        dataset = Dataset(
            name="Chrono Dataset",
            description="Chronobiology test dataset",
            dataset_type="PhenoMaster",
            metadata=metadata,
            animals=chrono_animals,
        )
        # Keep the built-in factors (Animal / Total / LightCycle) and add Group.
        dataset.factors["Group"] = chrono_group_factor

        datatable = Datatable(
            dataset=dataset,
            name="Main",
            description="Main datatable",
            variables=chrono_variable,
            df=chrono_df,
            metadata={},
        )
        dataset.datatables["Main"] = datatable
    return dataset


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


class TestGetChronobiologyResult:
    def test_group_mode_smoke(self, chrono_dataset, chrono_variable):
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Group",
            figsize=(8, 6),
        )
        assert isinstance(result, ChronobiologyResult)
        assert isinstance(result.report, str)
        assert "Zeitgeber-time profile" in result.report
        assert "Lomb" in result.report
        assert "cosinor" in result.report.lower()
        assert "Double-plotted actogram" in result.report
        # All plotted sections (incl. the actogram) emit an embedded image.
        assert "actogram skipped" not in result.report
        assert result.report.count("<img") >= 6

    def test_animal_count_correct_when_grouping_by_factor(self, chrono_dataset, chrono_variable):
        # Regression for A1: Animal column must be fetched even when grouping by
        # a non-Animal factor, so the summary reports the true animal count.
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Group",
            figsize=(8, 6),
        )
        text = _strip_html(result.report)
        match = re.search(r"Animals \(N\)\s+(\d+)", text)
        assert match is not None
        assert int(match.group(1)) == 6

    def test_single_level_group_renders_actogram(self, chrono_dataset, chrono_variable):
        # Regression for A3: a single-level grouping ("Total") must still render
        # an actogram instead of silently producing nothing.
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Total",
            figsize=(8, 6),
        )
        # An actogram image is emitted even though the grouping has one level.
        assert "Double-plotted actogram" in result.report
        assert "actogram skipped" not in result.report
        assert result.report.count("<img") >= 6

    def test_missing_datetime_skips_timeseries(self, chrono_dataset, chrono_variable, chrono_df):
        # Regression for A2: a datatable without a DateTime column must skip the
        # time-series sections gracefully instead of raising KeyError.
        df = chrono_df.drop(columns=["DateTime"])
        datatable = Datatable(
            dataset=chrono_dataset,
            name="NoDateTime",
            description="No DateTime",
            variables=chrono_variable,
            df=df,
            metadata={},
        )
        result = get_chronobiology_result(datatable, chrono_variable["Activity"], "Group", figsize=(8, 6))
        assert "time-series sections skipped" in result.report


class TestResultTables:
    """The ``tables`` payload used by the widget's 'Add Datatable' feature.

    Tables are only exposed when grouping by Animal (so every table has an
    "Animal" id column and is ANOVA-ready); grouping by a factor offers nothing.
    """

    def test_no_tables_when_grouping_by_factor(self, chrono_dataset, chrono_variable):
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Group",
            figsize=(8, 6),
        )
        # Grouping by a factor produces per-group aggregates that are not ANOVA-able,
        # so no result tables are offered.
        assert result.tables == {}

    def test_expected_tables_present_when_grouping_by_animal(self, chrono_dataset, chrono_variable):
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Animal",
            figsize=(8, 6),
        )
        assert "Per-animal parameters" in result.tables
        assert "Dominant periods" in result.tables
        assert "Cosinor parameters" in result.tables
        assert "Two-component cosinor" in result.tables
        # Summary is intentionally NOT addable (it is transposed metadata).
        assert "Summary" not in result.tables
        # Every exposed table carries an "Animal" id column.
        for rt in result.tables.values():
            assert rt.id_column == "Animal"
            assert "Animal" in rt.df.columns

    def test_per_animal_table_is_one_row_per_animal(self, chrono_dataset, chrono_variable):
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Animal",
            figsize=(8, 6),
        )
        rt = result.tables["Per-animal parameters"]
        assert rt.id_column == "Animal"
        assert "Animal" in rt.df.columns
        assert len(rt.df) == 6  # 6 animals, one row each
        assert set(rt.df["Animal"]) == {"M1", "M2", "M3", "M4", "M5", "M6"}
        for col in ("MESOR", "Amplitude", "Acrophase (ZT h)", "Dominant period (h)", "PR", "p_value"):
            assert col in rt.df.columns

    def test_per_group_id_column_renamed_from_group(self, chrono_dataset, chrono_variable):
        # When grouping by Animal, the per-group "Group" column becomes "Animal"
        # so the added table has an Animal column and is ANOVA-ready.
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Animal",
            figsize=(8, 6),
        )
        rt = result.tables["Cosinor parameters"]
        assert rt.id_column == "Animal"
        assert "Animal" in rt.df.columns
        assert "Group" not in rt.df.columns

    def test_to_datatable_builds_variables_and_attaches_factors(self, chrono_dataset, chrono_variable):
        result = get_chronobiology_result(
            chrono_dataset.datatables["Main"],
            chrono_variable["Activity"],
            "Animal",
            figsize=(8, 6),
        )
        datatable = result.tables["Per-animal parameters"].to_datatable(chrono_dataset, "Chrono per-animal")

        assert isinstance(datatable, Datatable)
        # Numeric parameter columns become Variable metadata; the id column does not.
        assert "Animal" not in datatable.variables
        for col in ("MESOR", "Amplitude", "Acrophase (ZT h)", "Dominant period (h)", "PR", "p_value"):
            assert col in datatable.variables
        # Nullable dtypes + categorical id (house rule).
        assert datatable.df["Animal"].dtype.name == "category"
        # Dataset factors are attached (the "Group" factor column is materialized);
        # the time-based LightCycle factor is skipped because there is no DateTime column.
        assert "Group" in datatable.df.columns

    def test_no_tables_without_datetime(self, chrono_dataset, chrono_variable, chrono_df):
        # Even when grouping by Animal, a datatable without DateTime yields no tables.
        df = chrono_df.drop(columns=["DateTime"])
        datatable = Datatable(
            dataset=chrono_dataset,
            name="NoDateTime",
            description="No DateTime",
            variables=chrono_variable,
            df=df,
            metadata={},
        )
        result = get_chronobiology_result(datatable, chrono_variable["Activity"], "Animal", figsize=(8, 6))
        assert result.tables == {}
