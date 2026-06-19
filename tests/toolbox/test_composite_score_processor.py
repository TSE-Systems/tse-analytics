"""Tests for tse_analytics.toolbox.composite_score.processor module."""

import matplotlib
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from tse_analytics.core.data.dafault_factor_builders import _get_default_animal_factor
from tse_analytics.toolbox.composite_score.processor import (
    CompositeScoreResult,
    _build_chart,
    compute_composite_scores,
    get_composite_score_result,
)

matplotlib.use("Agg")


class TestComputeCompositeScores:
    """Tests for the pure compute_composite_scores function."""

    def test_zscore_ranking(self):
        agg = pd.DataFrame({"Animal": ["A", "B", "C"], "X": [1.0, 2.0, 3.0], "Y": [1.0, 2.0, 3.0]})
        scores, warnings = compute_composite_scores(
            agg, ["X", "Y"], {"X": "higher", "Y": "higher"}, {"X": 1.0, "Y": 1.0}, "zscore"
        )
        assert warnings == []
        # Correlated, equally weighted -> monotonically increasing score.
        values = scores.set_index("Animal")["Score"]
        assert values["A"] < values["B"] < values["C"]

    def test_direction_inversion_changes_score(self):
        agg = pd.DataFrame({"Animal": ["A", "B", "C"], "X": [1.0, 2.0, 3.0], "Y": [1.0, 2.0, 3.0]})
        higher, _ = compute_composite_scores(
            agg, ["X", "Y"], {"X": "higher", "Y": "higher"}, {"X": 1.0, "Y": 1.0}, "zscore"
        )
        flipped, _ = compute_composite_scores(
            agg, ["X", "Y"], {"X": "lower", "Y": "higher"}, {"X": 1.0, "Y": 1.0}, "zscore"
        )
        # Flipping X cancels Y, collapsing the spread that existed before.
        assert higher.set_index("Animal").loc["C", "Score"] == 1.0
        assert np.allclose(flipped["Score"].to_numpy(), 0.0)

    def test_zero_variance_does_not_crash(self):
        agg = pd.DataFrame({"Animal": ["A", "B", "C"], "X": [5.0, 5.0, 5.0], "Y": [1.0, 2.0, 3.0]})
        scores, warnings = compute_composite_scores(
            agg, ["X", "Y"], {"X": "higher", "Y": "higher"}, {"X": 1.0, "Y": 1.0}, "zscore"
        )
        assert not scores["Score"].isna().any()
        assert any("zero variance" in message for message in warnings)

    def test_per_animal_missing_value_is_skipped(self):
        agg = pd.DataFrame({"Animal": ["A", "B", "C"], "X": [1.0, 2.0, 3.0], "Y": [1.0, np.nan, 3.0]})
        scores, _ = compute_composite_scores(
            agg, ["X", "Y"], {"X": "higher", "Y": "higher"}, {"X": 1.0, "Y": 1.0}, "zscore"
        )
        # B has no Y, so its score is X's normalized value alone (finite, not NaN).
        assert not scores["Score"].isna().any()

    def test_weights_affect_score(self):
        agg = pd.DataFrame({"Animal": ["A", "B"], "X": [0.0, 1.0], "Y": [1.0, 0.0]})
        scores, _ = compute_composite_scores(
            agg, ["X", "Y"], {"X": "higher", "Y": "higher"}, {"X": 3.0, "Y": 1.0}, "zscore"
        )
        # X weighted heavier -> B (high X) outranks A.
        values = scores.set_index("Animal")["Score"]
        assert values["B"] > values["A"]


class TestGetCompositeScoreResult:
    """Tests for the datatable-driven orchestrator."""

    def test_returns_result(self, analysis_dataset):
        datatable = analysis_dataset.datatables["Main"]
        result = get_composite_score_result(
            datatable,
            ["Metabolism", "Activity"],
            {"Metabolism": "higher", "Activity": "higher"},
            {"Metabolism": 1.0, "Activity": 1.0},
            "zscore",
            "Group",
            (8, 6),
        )
        assert isinstance(result, CompositeScoreResult)
        assert "<img" in result.report
        assert "Composite performance score" in result.report

    def test_scores_df_shape(self, analysis_dataset):
        datatable = analysis_dataset.datatables["Main"]
        result = get_composite_score_result(
            datatable,
            ["Metabolism", "Activity"],
            {"Metabolism": "higher", "Activity": "higher"},
            {"Metabolism": 1.0, "Activity": 1.0},
            "zscore",
            "Animal",
        )
        assert len(result.scores_df) == 6
        assert "Score" in result.scores_df.columns
        assert sorted(result.scores_df["Rank"].to_list()) == [1, 2, 3, 4, 5, 6]

    def test_minmax_normalization(self, analysis_dataset):
        datatable = analysis_dataset.datatables["Main"]
        result = get_composite_score_result(
            datatable,
            ["Metabolism", "Activity"],
            {"Metabolism": "higher", "Activity": "higher"},
            {"Metabolism": 1.0, "Activity": 1.0},
            "minmax",
            "Group",
        )
        assert isinstance(result, CompositeScoreResult)
        # "Color by" is used only to color the bars: the factor is attached to the
        # scores for coloring, but no group-summary table is produced.
        assert "Group" in result.scores_df.columns
        assert "Group summary" not in result.report
        assert "<img" in result.report

    def test_color_by_does_not_change_scores(self, analysis_dataset):
        datatable = analysis_dataset.datatables["Main"]
        args = (
            datatable,
            ["Metabolism", "Activity"],
            {"Metabolism": "higher", "Activity": "higher"},
            {"Metabolism": 1.0, "Activity": 1.0},
            "zscore",
        )
        pooled = get_composite_score_result(*args, "Animal")
        colored = get_composite_score_result(*args, "Group")
        # Normalization is always pooled across all animals, so the "Color by"
        # selection (coloring only) must not change the per-animal scores.
        pooled_scores = pooled.scores_df.set_index("Animal")["Score"]
        colored_scores = colored.scores_df.set_index("Animal")["Score"]
        assert np.allclose(
            pooled_scores.to_numpy(dtype="float64"),
            colored_scores.loc[pooled_scores.index].to_numpy(dtype="float64"),
        )

    def test_color_by_animal_uses_animal_colors(self, analysis_dataset):
        dataset = analysis_dataset
        dataset.factors["Animal"] = _get_default_animal_factor(dataset.animals)
        datatable = dataset.datatables["Main"]
        result = get_composite_score_result(
            datatable,
            ["Metabolism", "Activity"],
            {"Metabolism": "higher", "Activity": "higher"},
            {"Metabolism": 1.0, "Activity": 1.0},
            "zscore",
            "Animal",
        )
        # "Animal" is the row label, so it must not be duplicated as an extra column.
        assert list(result.scores_df.columns).count("Animal") == 1

        # Each bar is colored by its own animal's color from the Animal factor.
        palette = {level.name: level.color for level in dataset.factors["Animal"].levels.values()}
        figure = _build_chart(datatable, result.scores_df, "Animal", (8, 6))
        bars = figure.axes[0].patches
        animal_order = result.scores_df["Animal"].astype(str).to_list()
        assert len(bars) == len(animal_order)
        for animal, bar in zip(animal_order, bars, strict=True):
            assert np.allclose(bar.get_facecolor(), mcolors.to_rgba(palette[animal]))

    def test_single_variable_returns_none(self, analysis_dataset):
        datatable = analysis_dataset.datatables["Main"]
        result = get_composite_score_result(
            datatable,
            ["Metabolism"],
            {"Metabolism": "higher"},
            {"Metabolism": 1.0},
            "zscore",
            "Animal",
        )
        assert result is None
