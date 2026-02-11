from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import chisquare, kruskal

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils import get_html_image_from_figure, get_html_table


@dataclass
class IntelliCagePlacePreferenceResult:
    report: str
    visit_counts: pd.DataFrame
    normalized_visit_counts: pd.DataFrame
    visit_results: pd.DataFrame
    duration_results: pd.DataFrame


def get_intellicage_place_preference_result(
    dataset: Dataset,
    df: pd.DataFrame,
    figsize: tuple[float, float] | None = None,
) -> IntelliCagePlacePreferenceResult:
    # Create a figure with a tight layout
    visit_counts_figure = plt.Figure(figsize=figsize, layout="tight")
    visit_counts_axes = visit_counts_figure.subplots(1, 2, sharey=False)

    visit_results, visit_counts = _analyze_visits(df)
    duration_results = _analyze_durations(df)

    sns.heatmap(
        visit_counts,
        annot=True,
        cmap="YlGnBu",
        fmt="d",
        ax=visit_counts_axes[0],
    )
    visit_counts_axes[0].set(
        title="Visit Counts per Corner",
    )

    normalized_visit_counts = visit_counts.div(
        visit_counts.sum(axis=1),
        axis=0,
    )
    normalized_visit_counts.plot(
        kind="barh",
        stacked=True,
        ax=visit_counts_axes[1],
        # sharey=True,
    )
    visit_counts_axes[1].invert_yaxis()
    visit_counts_axes[1].set(
        title="Proportional Visit Distribution",
    )

    visit_duration_figure = plt.Figure(figsize=figsize, layout="tight")
    visit_duration_axes = visit_duration_figure.subplots(1, 1)
    sns.boxplot(x="Corner", y="VisitDuration", data=df, ax=visit_duration_axes)
    visit_duration_axes.set(
        title="Visit Duration by Corner",
        xlabel="Corner",
        ylabel="Duration (s)",
    )

    html_template = """
                    {visit_counts}
                    {visit_duration}
                    <div class="horizontal-container">
                    {visit_results}
                    {duration_results}
                    </div>
                    """

    report = html_template.format(
        visit_counts=get_html_image_from_figure(visit_counts_figure),
        visit_duration=get_html_image_from_figure(visit_duration_figure),
        visit_results=get_html_table(visit_results, "Visit Results", index=False),
        duration_results=get_html_table(duration_results, "Visit Duration Results", index=False),
    )

    return IntelliCagePlacePreferenceResult(
        report=report,
        visit_counts=visit_counts,
        normalized_visit_counts=normalized_visit_counts,
        visit_results=visit_results,
        duration_results=duration_results,
    )


def _analyze_visits(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Analyze visit counts using chi-square goodness-of-fit test"""
    visit_counts = df.groupby(["Animal", "Corner"], observed=True).size().unstack(fill_value=0)
    visit_counts.sort_values(by=["Animal"], inplace=True)

    results = []
    for animal in visit_counts.index:
        observed = visit_counts.loc[animal].values
        total = observed.sum()
        expected = [total / len(observed)] * len(observed)
        chi2, p = chisquare(observed, expected)

        results.append({"Animal": animal, "chi2": chi2, "p_value": p, "significant": p < 0.05})

    return pd.DataFrame(results), visit_counts


def _analyze_durations(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze duration distributions using Kruskal-Wallis test"""
    results = []
    for animal in df["Animal"].unique():
        animal_data = df[df["Animal"] == animal]
        corners = animal_data["Corner"].unique()

        if len(corners) < 2:
            continue  # Skip mice with only one corner visited

        groups = [animal_data[animal_data["Corner"] == corner]["VisitDuration"].values for corner in corners]
        h_stat, p_value = kruskal(*groups)

        results.append({
            "Animal": animal,
            "h_statistic": h_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
        })

    return pd.DataFrame(results)
