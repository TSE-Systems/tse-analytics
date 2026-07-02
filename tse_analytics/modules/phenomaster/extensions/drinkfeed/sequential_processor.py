import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.phenomaster.extensions.drinkfeed.drinkfeed_settings import DrinkFeedSettings


def process_drinkfeed_sequences(
    datatable: Datatable,
    settings: DrinkFeedSettings,
    diets_dict: dict[str, float],
) -> tuple[Datatable, Datatable]:
    long_df = pd.melt(
        datatable.df,
        id_vars=["DateTime", "Timedelta", "Animal", "Box"],
        var_name="Sensor",
        value_name="Value",
    )
    long_df = long_df.sort_values(by=["Timedelta"]).reset_index(drop=True)
    long_df["Sensor"] = long_df["Sensor"].astype("category")

    # Filter out zero values
    long_df = long_df.loc[long_df["Value"] != 0]
    long_df = long_df.sort_values(by=["Timedelta"]).reset_index(drop=True)

    sensors = long_df["Sensor"].unique().tolist()

    events_parts: list[pd.DataFrame] = []
    episodes_parts: list[pd.DataFrame] = []
    for animal_id in datatable.dataset.animals.keys():
        animal_df = long_df[long_df["Animal"] == animal_id]
        animal_events_df, animal_episodes_df = _process_animal(
            animal_id,
            animal_df,
            sensors,
            settings,
        )
        if not animal_events_df.empty:
            events_parts.append(animal_events_df)
        if not animal_episodes_df.empty:
            episodes_parts.append(animal_episodes_df)

    events_df = pd.concat(events_parts, ignore_index=True) if events_parts else pd.DataFrame()
    episodes_df = pd.concat(episodes_parts, ignore_index=True) if episodes_parts else pd.DataFrame()

    # Add caloric value column
    episodes_df.insert(
        episodes_df.columns.get_loc("Quantity") + 1,
        "Quantity[kcal]",
        episodes_df["Animal"].map(diets_dict),
    )
    episodes_df["Quantity[kcal]"] = episodes_df["Quantity[kcal]"] * episodes_df["Quantity"]

    # convert types
    episodes_df = episodes_df.astype({
        "Sensor": "category",
        "Animal": "category",
        "Quantity[kcal]": "Float64",
        "Rate": "Float64",
    })

    events_df = events_df.sort_values(by=["Timedelta"]).reset_index(drop=True)
    episodes_df = episodes_df.sort_values(by=["Timedelta"]).reset_index(drop=True)

    events_datatable = Datatable.from_dataframe(
        datatable.dataset,
        "DrinkFeedEvents",
        events_df,
        origin="DrinkFeedEvents",
        description="DrinkFeed events datatable",
        variables={
            "Value": Variable(
                "Value",
                "",
                "Sensor value",
                "Float64",
                Aggregation.SUM,
                False,
            ),
        },
        apply_factors=False,
        normalize_dtypes=False,
    )

    episodes_datatable = Datatable.from_dataframe(
        datatable.dataset,
        "DrinkFeedEpisodes",
        episodes_df,
        origin="DrinkFeedEpisodes",
        description="DrinkFeed episodes datatable",
        variables={
            "Duration[minutes]": Variable(
                "Duration[minutes]",
                "minutes",
                "Episode duration",
                "Float64",
                Aggregation.SUM,
                False,
            ),
            "Interval[minutes]": Variable(
                "Interval[minutes]",
                "minutes",
                "Inter-meal interval",
                "Float64",
                Aggregation.MEAN,
                False,
            ),
            "Quantity": Variable(
                "Quantity",
                "g or ml",
                "Consumed quantity",
                "Float64",
                Aggregation.SUM,
                False,
            ),
            "Quantity[kcal]": Variable(
                "Quantity[kcal]",
                "kcal",
                "Quantity in kilocalories",
                "Float64",
                Aggregation.SUM,
                False,
            ),
            "Rate": Variable(
                "Rate",
                "g/min or ml/min",
                "Consumption rate per minute",
                "Float64",
                Aggregation.MEAN,
                False,
            ),
        },
        apply_factors=False,
        normalize_dtypes=False,
    )

    return events_datatable, episodes_datatable


# (metric column, unit, description, aggregation) for the per-sensor episode variables.
# A unit of None is resolved per sensor (ml / ml/min for Drink*, g / g/min for Feed*).
_EPISODE_METRICS: list[tuple[str, str | None, str, Aggregation]] = [
    ("Duration[minutes]", "minutes", "Episode duration", Aggregation.SUM),
    ("Interval[minutes]", "minutes", "Inter-meal interval", Aggregation.MEAN),
    ("Quantity", None, "Consumed quantity", Aggregation.SUM),
    ("Quantity[kcal]", "kcal", "Quantity in kilocalories", Aggregation.SUM),
    ("Rate", None, "Consumption rate per minute", Aggregation.MEAN),
]


def build_wide_episodes_datatable(episodes_datatable: Datatable, name: str) -> Datatable:
    """Reshape the long, per-sensor DrinkFeed episodes table into a wide datatable.

    Instead of a ``Sensor`` column plus generic metric columns (``Quantity``, ``Rate``, …), every
    metric becomes a per-sensor column (e.g. ``Drink1Quantity``, ``Feed2Rate``). Each episode
    remains its own row keyed by ``DateTime``/``Timedelta``/``Animal``; only the row's own sensor
    columns are filled, the rest are ``<NA>``.

    Args:
        episodes_datatable: The long episodes datatable returned by
            :func:`process_drinkfeed_sequences`.
        name: Name for the resulting datatable.

    Returns:
        A new wide per-sensor episodes ``Datatable``.
    """
    wide_df, variables = _reshape_episodes_to_wide(episodes_datatable.df)
    return Datatable.from_dataframe(
        episodes_datatable.dataset,
        name,
        wide_df,
        origin="DrinkFeedEpisodes",
        description="DrinkFeed episodes datatable (per-sensor)",
        variables=variables,
        apply_factors=False,
        normalize_dtypes=False,
    )


def _reshape_episodes_to_wide(long_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Variable]]:
    """Spread a long per-episode frame into per-sensor metric columns (one row per episode)."""
    id_cols = ["DateTime", "Timedelta", "Animal"]

    if long_df.empty:
        return long_df[id_cols].copy(), {}

    src = long_df.reset_index(drop=True)
    wide = src[id_cols].copy()
    variables: dict[str, Variable] = {}

    for sensor in sorted(src["Sensor"].dropna().unique()):
        mask = src["Sensor"] == sensor
        is_drink = "Drink" in sensor
        for metric, unit, description, aggregation in _EPISODE_METRICS:
            column = f"{sensor}{metric}"
            wide[column] = src[metric].where(mask)
            if unit is None:
                resolved_unit = ("ml/min" if is_drink else "g/min") if metric == "Rate" else ("ml" if is_drink else "g")
            else:
                resolved_unit = unit
            variables[column] = Variable(
                column,
                resolved_unit,
                f"{sensor} {description}",
                "Float64",
                aggregation,
                False,
            )

    return wide, variables


def _process_animal(
    animal_id: str,
    df: pd.DataFrame,
    sensors: list[str],
    settings: DrinkFeedSettings,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    events_parts: list[pd.DataFrame] = []
    episodes_parts: list[pd.DataFrame] = []
    for sensor in sensors:
        # Ignore Weight sensor
        if sensor == "Weight":
            continue

        sensor_df = df[df["Sensor"] == sensor]
        sensor_events_df = _extract_sensor_events(
            sensor_df,
            sensor,
            settings,
        )
        if not sensor_events_df.empty:
            events_parts.append(sensor_events_df)

        sensor_episodes_df = _extract_sensor_episodes(
            animal_id,
            sensor_events_df,
            sensor,
        )
        if not sensor_episodes_df.empty:
            episodes_parts.append(sensor_episodes_df)

    animal_events_df = pd.concat(events_parts, ignore_index=True) if events_parts else pd.DataFrame()
    animal_episodes_df = pd.concat(episodes_parts, ignore_index=True) if episodes_parts else pd.DataFrame()
    return animal_events_df, animal_episodes_df


def _extract_sensor_events(
    df: pd.DataFrame,
    sensor: str,
    settings: DrinkFeedSettings,
) -> pd.DataFrame:
    events_df = df.copy()

    if events_df.empty:
        events_df.insert(1, "EpisodeId", pd.array([], dtype="UInt64"))
        events_df.insert(2, "Interval", pd.array([], dtype="timedelta64[ns]"))
        return events_df

    timedelta = pd.Timedelta(
        hours=settings.intermeal_interval.hour,
        minutes=settings.intermeal_interval.minute,
        seconds=settings.intermeal_interval.second,
    )

    intervals = events_df["Timedelta"].diff()
    new_episode = intervals > timedelta
    episode_ids = new_episode.astype("Int8").cumsum().astype("UInt64")

    events_df.insert(1, "EpisodeId", episode_ids)
    events_df.insert(2, "Interval", intervals)

    events_df = _find_invalid_episodes(
        events_df, settings.drinking_minimum_amount if "Drink" in sensor else settings.feeding_minimum_amount
    )

    return events_df


def _extract_sensor_episodes(
    animal_id: str,
    events_df: pd.DataFrame,
    sensor: str,
) -> pd.DataFrame:
    valid_events = events_df[events_df["EpisodeId"].notna()]

    if valid_events.empty:
        return pd.DataFrame(
            columns=[
                "DateTime",
                "Timedelta",
                "Animal",
                "Sensor",
                "Id",
                "Duration",
                "Duration[minutes]",
                "Interval",
                "Interval[minutes]",
                "Quantity",
                "Rate",
            ],
        )

    grouped = valid_events.groupby("EpisodeId", sort=False).agg(
        DateTime=("DateTime", "first"),
        Start=("Timedelta", "first"),
        End=("Timedelta", "last"),
        Quantity=("Value", "sum"),
        Count=("Value", "size"),
    )

    episodes = pd.DataFrame({
        "DateTime": grouped["DateTime"],
        "Timedelta": grouped["Start"],
        "Animal": animal_id,
        "Sensor": sensor,
        "Id": grouped.index,
    })

    duration = grouped["End"] - grouped["Start"]
    # Single-event episodes get NaT duration
    duration = duration.where(grouped["Count"] > 1)
    episodes["Duration"] = duration

    duration_minutes = (duration.dt.total_seconds() / 60).round(3).astype("Float64")
    episodes["Duration[minutes]"] = duration_minutes

    # Inter-meal interval = next_start - current_start + current_duration (NaT for single-event and last episode)
    next_start = grouped["Start"].shift(-1)
    imi = next_start - grouped["Start"] + duration
    episodes["Interval"] = imi
    episodes["Interval[minutes]"] = (imi.dt.total_seconds() / 60).round(3).astype("Float64")

    episodes["Quantity"] = grouped["Quantity"]
    episodes["Quantity"] = episodes["Quantity"].astype("Float64")

    # Rate = quantity / duration_minutes (NaN where duration is NaT)
    episodes["Rate"] = grouped["Quantity"] / duration_minutes

    return episodes


def _find_invalid_episodes(events_df: pd.DataFrame, minimum_amount: float) -> pd.DataFrame:
    valid = events_df["EpisodeId"].notna()
    if valid.any():
        episode_sum = events_df.loc[valid].groupby("EpisodeId")["Value"].transform("sum")
        events_df.loc[valid, "EpisodeId"] = events_df.loc[valid, "EpisodeId"].where(episode_sum >= minimum_amount)
    return events_df
