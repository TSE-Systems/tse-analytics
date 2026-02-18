"""Tests for tse_analytics.toolbox.actogram.processor module."""

import datetime

import matplotlib

matplotlib.use("Agg")

import matplotlib.axes
import matplotlib.figure
import numpy as np
import pandas as pd
import pytest
from tse_analytics.core.data.binning import TimeCyclesBinningSettings
from tse_analytics.toolbox.actogram.processor import (
    ActogramResult,
    dataframe_to_actogram,
    get_actogram_result,
    plot_enhanced_actogram,
)


@pytest.fixture
def actogram_df(analysis_animals):
    """DataFrame with 6 animals x 72 hourly timepoints across 3 days (432 rows).

    Activity follows a sinusoidal circadian pattern for realistic data.
    """
    rng = np.random.default_rng(42)
    base_time = pd.Timestamp("2024-01-01")
    interval = pd.Timedelta("1h")

    rows = []
    for i in range(72):
        hour_of_day = i % 24
        # Sinusoidal circadian pattern: peak at hour 14, trough at hour 2
        circadian = np.sin(2 * np.pi * (hour_of_day - 8) / 24)
        for animal_id, animal in analysis_animals.items():
            group = animal.properties["group"]
            base_activity = 120.0 if group == "Control" else 180.0
            base_metabolism = 5.0 if group == "Control" else 8.0

            rows.append({
                "Animal": animal_id,
                "DateTime": base_time + i * interval,
                "Timedelta": i * interval,
                "Bin": i,
                "Activity": max(0, base_activity * (1 + 0.5 * circadian) + rng.normal(0, 10)),
                "Metabolism": base_metabolism + rng.normal(0, 0.5),
                "Group": group,
            })

    df = pd.DataFrame(rows)
    df["Animal"] = df["Animal"].astype("category")
    df["Timedelta"] = pd.to_timedelta(df["Timedelta"])
    df["Group"] = df["Group"].astype("category")
    df["Run"] = pd.Categorical([1] * len(df))
    return df


class TestDataframeToActogram:
    """Tests for dataframe_to_actogram function."""

    def test_output_shape_default_bins(self, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        activity_array, unique_days = dataframe_to_actogram(actogram_df, variable, bins_per_day=24)

        assert activity_array.shape == (3, 24)
        assert len(unique_days) == 3

    def test_output_shape_custom_bins(self, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        activity_array, unique_days = dataframe_to_actogram(actogram_df, variable, bins_per_day=48)

        assert activity_array.shape == (3, 48)
        assert len(unique_days) == 3

    def test_output_shape_fewer_bins(self, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        activity_array, unique_days = dataframe_to_actogram(actogram_df, variable, bins_per_day=6)

        assert activity_array.shape == (3, 6)
        assert len(unique_days) == 3

    def test_values_are_nonnegative(self, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        activity_array, _ = dataframe_to_actogram(actogram_df, variable)

        assert np.all(activity_array >= 0)

    def test_unique_days_are_sorted_dates(self, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        _, unique_days = dataframe_to_actogram(actogram_df, variable)

        assert all(isinstance(d, datetime.date) for d in unique_days)
        assert unique_days == sorted(unique_days)

    def test_single_day_data(self, analysis_df, analysis_variables):
        variable = analysis_variables["Activity"]
        activity_array, unique_days = dataframe_to_actogram(analysis_df, variable)

        assert activity_array.shape == (1, 24)
        assert len(unique_days) == 1


class TestPlotEnhancedActogram:
    """Tests for plot_enhanced_actogram function."""

    def test_returns_figure_and_axes(self):
        data = np.random.default_rng(42).random((3, 24))
        fig, ax = plot_enhanced_actogram(data, figsize=(8, 6))

        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(ax, matplotlib.axes.Axes)

    def test_1d_input_handling(self):
        data = np.random.default_rng(42).random(48)
        fig, ax = plot_enhanced_actogram(data, figsize=(8, 6))

        assert isinstance(fig, matplotlib.figure.Figure)

    def test_custom_title(self):
        data = np.random.default_rng(42).random((3, 24))
        _, ax = plot_enhanced_actogram(data, figsize=(8, 6), title="My Actogram")

        assert ax.get_title() == "My Actogram"

    def test_custom_day_labels(self):
        data = np.random.default_rng(42).random((3, 24))
        day_labels = ["2024-01-01", "2024-01-02", "2024-01-03"]
        _, ax = plot_enhanced_actogram(data, figsize=(8, 6), days=day_labels)

        tick_labels = [t.get_text() for t in ax.get_yticklabels()]
        assert tick_labels == day_labels[::-1]

    def test_with_highlight_periods(self):
        data = np.random.default_rng(42).random((3, 24))
        periods = [{"start": 19, "end": 24, "color": "gray", "alpha": 0.2}]
        fig, ax = plot_enhanced_actogram(data, figsize=(8, 6), highlight_periods=periods)

        assert isinstance(fig, matplotlib.figure.Figure)

    def test_xlim_is_double_width(self):
        bins_per_day = 24
        data = np.random.default_rng(42).random((3, bins_per_day))
        _, ax = plot_enhanced_actogram(data, figsize=(8, 6))

        xlim = ax.get_xlim()
        assert xlim == (0, 2 * bins_per_day)


class TestGetActogramResult:
    """Integration tests for get_actogram_result function."""

    def test_returns_actogram_result(self, analysis_dataset, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        result = get_actogram_result(
            dataset=analysis_dataset,
            df=actogram_df,
            variable=variable,
            bins_per_hour=1,
            figsize=(8, 6),
        )

        assert isinstance(result, ActogramResult)

    def test_report_contains_image(self, analysis_dataset, actogram_df, analysis_variables):
        variable = analysis_variables["Activity"]
        result = get_actogram_result(
            dataset=analysis_dataset,
            df=actogram_df,
            variable=variable,
            bins_per_hour=1,
            figsize=(8, 6),
        )

        assert "<img" in result.report

    @pytest.mark.parametrize("bins_per_hour", [1, 2, 4, 6])
    def test_bins_per_hour_variations(self, analysis_dataset, actogram_df, analysis_variables, bins_per_hour):
        variable = analysis_variables["Activity"]
        result = get_actogram_result(
            dataset=analysis_dataset,
            df=actogram_df,
            variable=variable,
            bins_per_hour=bins_per_hour,
            figsize=(8, 6),
        )

        assert isinstance(result, ActogramResult)

    def test_single_day_data(self, analysis_dataset, analysis_df, analysis_variables):
        variable = analysis_variables["Activity"]
        result = get_actogram_result(
            dataset=analysis_dataset,
            df=analysis_df,
            variable=variable,
            bins_per_hour=1,
            figsize=(8, 6),
        )

        assert isinstance(result, ActogramResult)

    def test_dark_cycle_before_light_cycle(self, analysis_dataset, actogram_df, analysis_variables):
        analysis_dataset.binning_settings.time_cycles_settings = TimeCyclesBinningSettings(
            light_cycle_start=datetime.time(7, 0),
            dark_cycle_start=datetime.time(3, 0),
        )
        variable = analysis_variables["Activity"]
        result = get_actogram_result(
            dataset=analysis_dataset,
            df=actogram_df,
            variable=variable,
            bins_per_hour=1,
            figsize=(8, 6),
        )

        assert isinstance(result, ActogramResult)
        assert "<img" in result.report

    def test_metabolism_variable(self, analysis_dataset, actogram_df, analysis_variables):
        variable = analysis_variables["Metabolism"]
        result = get_actogram_result(
            dataset=analysis_dataset,
            df=actogram_df,
            variable=variable,
            bins_per_hour=1,
            figsize=(8, 6),
        )

        assert isinstance(result, ActogramResult)
