import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from xarray.core import variable

from tse_analytics.core.data.shared import Variable


def dataframe_to_actogram(
    df: pd.DataFrame,
    variable: Variable,
    bins_per_day=24,
):
    """
    Convert DataFrame with timestamp and activity into format suitable for actogram
    """
    df = df.copy()

    # Extract day information
    df["Date"] = df["DateTime"].dt.date
    df["Time"] = df["DateTime"].dt.hour * 60 + df["DateTime"].dt.minute

    # Determine bin for each timestamp
    minutes_per_bin = 24 * 60 / bins_per_day
    df["Bin"] = (df["Time"] / minutes_per_bin).astype(int)

    df = df.groupby(["Date", "Bin"], dropna=False, observed=False).aggregate({
        variable.name: variable.aggregation,
    })
    df.reset_index(inplace=True)

    # Get unique days
    unique_days = sorted(df["Date"].unique())
    days_count = len(unique_days)

    # Create empty activity array
    activity_array = np.zeros((days_count, bins_per_day))

    # Fill the array with activity data
    for i, day in enumerate(unique_days):
        day_data = df[df["Date"] == day]
        for _, row in day_data.iterrows():
            bin_idx = row["Bin"]
            if bin_idx < bins_per_day:  # Ensure index is within bounds
                activity_array[i, bin_idx] = row[variable.name]

    return activity_array, unique_days


# Enhanced version with customization
def plot_enhanced_actogram(
    activity_data,
    days=None,
    binsize=None,
    title="Actogram",
    bar_color="black",
    highlight_periods=None,
):
    """
    Plot a more customized double-plotted actogram

    Parameters:
    -----------
    activity_data : array-like
        Activity data with shape (days, bins_per_day)
    days : list, optional
        List of day labels
    binsize : float, optional
        Size of each time bin in hours
    title : str
        Title of the plot
    bar_color : str
        Color of the activity bars
    highlight_periods : list of dict, optional
        List of periods to highlight, each with keys:
        - 'start': start hour (float)
        - 'end': end hour (float)
        - 'color': highlight color (str)
        - 'alpha': transparency (float)
    """
    if activity_data.ndim == 1:
        # Convert to 2D if 1D array is provided
        bins_per_day = len(activity_data) // 2  # Assuming the data spans 2 days
        days_count = 2
        activity_data = activity_data.reshape(days_count, bins_per_day)
    else:
        days_count, bins_per_day = activity_data.shape

    # Create day labels if not provided
    if days is None:
        days = [f"Day {i + 1}" for i in range(days_count)]

    # Create time labels if binsize is provided
    if binsize:
        # time_labels = [f"{int(i * binsize)}:00" for i in range(0, 24, int(binsize * 2))]
        # time_labels = [f"{i * binsize}" for i in range(0, 24, int(binsize * 2))]
        # TODO: check if there is a nicer solution
        time_labels = [f"{i}" for i in range(0, 26, 2)]
        xticks = np.linspace(0, bins_per_day, len(time_labels))
    else:
        time_labels = [f"{i}h" for i in range(0, 24, 4)]
        xticks = np.linspace(0, bins_per_day, len(time_labels))

    # Create the figure
    fig, ax = plt.subplots(figsize=(14, 10))

    # Add highlight periods if specified
    if highlight_periods:
        for period in highlight_periods:
            start_bin = int(period["start"] / 24 * bins_per_day)
            end_bin = int(period["end"] / 24 * bins_per_day)

            # Add highlight for both copies
            ax.axvspan(start_bin, end_bin, color=period["color"], alpha=period.get("alpha", 0.2), zorder=1)
            ax.axvspan(
                start_bin + bins_per_day,
                end_bin + bins_per_day,
                color=period["color"],
                alpha=period.get("alpha", 0.2),
                zorder=1,
            )

    # For double plotting, we duplicate each row and offset it
    for i in range(days_count):
        # First day's data
        if i > 0:  # Skip first day for better alignment
            ax.bar(
                np.arange(bins_per_day),
                activity_data[i - 1],
                width=1,
                color=bar_color,
                align="center",
                bottom=days_count - i,
                alpha=1,
                zorder=3,
                edgecolor="none",
            )

        # Second day's data (offset to continue after first day)
        ax.bar(
            np.arange(bins_per_day, 2 * bins_per_day),
            activity_data[i],
            width=1,
            color=bar_color,
            align="center",
            bottom=days_count - i,
            alpha=1,
            zorder=3,
            edgecolor="none",
        )

    # Set ticks and labels
    ax.set_xticks(np.concatenate([xticks, xticks + bins_per_day]))
    ax.set_xticklabels(time_labels + time_labels)
    ax.set_yticks(np.arange(1, days_count + 1))
    ax.set_yticklabels(days[::-1])  # Reverse to have day 1 at the top

    # Set plot limits
    ax.set_xlim(0, 2 * bins_per_day)
    ax.set_ylim(0, days_count + 1)

    # Labels and title
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Day")
    ax.set_title(title)

    # Add vertical lines to separate days
    ax.axvline(bins_per_day, color="gray", linestyle="-", alpha=0.7, zorder=2)

    # Add grid for better readability
    ax.grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    return fig, ax
