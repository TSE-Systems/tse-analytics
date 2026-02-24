import pandas as pd

from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_bin_data import DrinkFeedBinData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings


def _find_invalid_episodes(events_df: pd.DataFrame, minimum_amount: float) -> pd.DataFrame:
    valid = events_df["EpisodeId"].notna()
    if valid.any():
        episode_sum = events_df.loc[valid].groupby("EpisodeId")["Value"].transform("sum")
        events_df.loc[valid, "EpisodeId"] = events_df.loc[valid, "EpisodeId"].where(episode_sum >= minimum_amount)
    return events_df


def process_drinkfeed_sequences(
    drinkfeed_data: DrinkFeedBinData,
    long_df: pd.DataFrame,
    settings: DrinkFeedSettings,
    diets_dict: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    long_df = long_df.loc[long_df["Value"] != 0]

    long_df = long_df.sort_values(by=["DateTime"])
    long_df = long_df.reset_index(drop=True)

    sensors = long_df["Sensor"].unique().tolist()

    events_parts: list[pd.DataFrame] = []
    episodes_parts: list[pd.DataFrame] = []
    for animal_id in drinkfeed_data.dataset.animals.keys():
        animal_df = long_df[long_df["Animal"] == animal_id]
        animal_events_df, animal_episodes_df = _process_animal(
            animal_id,
            animal_df,
            sensors,
            settings,
            drinkfeed_data.raw_df["DateTime"].iloc[0],
        )
        events_parts.append(animal_events_df)
        episodes_parts.append(animal_episodes_df)

    events_df = pd.concat(events_parts, ignore_index=True) if events_parts else pd.DataFrame()
    episodes_df = pd.concat(episodes_parts, ignore_index=True) if episodes_parts else pd.DataFrame()

    # Add caloric value column
    episodes_df.insert(
        episodes_df.columns.get_loc("Quantity") + 1, "Quantity-kcal", episodes_df["Animal"].map(diets_dict)
    )
    episodes_df["Quantity-kcal"] = episodes_df["Quantity-kcal"] * episodes_df["Quantity"]

    # convert types
    episodes_df = episodes_df.astype({
        "Sensor": "category",
        "Animal": "category",
        "Id": int,
        "Duration": "timedelta64[ns]",
        "Gap": "timedelta64[ns]",
        "Rate": "float64",
    })

    return events_df, episodes_df


def _process_animal(
    animal_id: str,
    df: pd.DataFrame,
    sensors: list[str],
    settings: DrinkFeedSettings,
    start_timestamp: pd.Timestamp,
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
        events_parts.append(sensor_events_df)

        sensor_episodes_df = _extract_sensor_episodes(
            animal_id,
            start_timestamp,
            sensor_events_df,
            sensor,
        )
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
        events_df.insert(1, "EpisodeId", pd.array([], dtype="Int64"))
        events_df.insert(2, "Gap", pd.array([], dtype="timedelta64[ns]"))
        return events_df

    timedelta = pd.Timedelta(
        hours=settings.intermeal_interval.hour,
        minutes=settings.intermeal_interval.minute,
        seconds=settings.intermeal_interval.second,
    )

    gaps = events_df["DateTime"].diff()
    new_episode = gaps > timedelta
    episode_ids = new_episode.cumsum().astype("Int64")

    events_df.insert(1, "EpisodeId", episode_ids.values)
    events_df.insert(2, "Gap", gaps.values)

    events_df = _find_invalid_episodes(
        events_df, settings.drinking_minimum_amount if "Drink" in sensor else settings.feeding_minimum_amount
    )

    return events_df


def _extract_sensor_episodes(
    animal_id: str,
    start_timestamp: pd.Timestamp,
    events_df: pd.DataFrame,
    sensor: str,
) -> pd.DataFrame:
    valid_events = events_df[events_df["EpisodeId"].notna()]

    if valid_events.empty:
        return pd.DataFrame(
            columns=[
                "Sensor",
                "Animal",
                "Id",
                "Start",
                "Offset",
                "Offset[minutes]",
                "Duration",
                "Duration[minutes]",
                "Gap",
                "Gap[minutes]",
                "Quantity",
                "Rate",
            ],
        )

    grouped = valid_events.groupby("EpisodeId", sort=False).agg(
        Start=("DateTime", "first"),
        End=("DateTime", "last"),
        Quantity=("Value", "sum"),
        Count=("Value", "size"),
    )

    episodes = pd.DataFrame({
        "Sensor": sensor,
        "Animal": animal_id,
        "Id": grouped.index,
        "Start": grouped["Start"].values,
    })

    offset = grouped["Start"] - start_timestamp
    episodes["Offset"] = offset.values
    episodes["Offset[minutes]"] = (offset.dt.total_seconds() / 60).round(3).values

    duration = grouped["End"] - grouped["Start"]
    # Single-event episodes get NaT duration
    duration = duration.where(grouped["Count"] > 1)
    episodes["Duration"] = duration.values

    duration_minutes = duration.dt.total_seconds() / 60
    duration_minutes = duration_minutes.round(3)
    episodes["Duration[minutes]"] = duration_minutes.values

    # Gap = next_start - current_start + current_duration (NaT for single-event and last episode)
    next_start = grouped["Start"].shift(-1)
    gap = next_start - grouped["Start"] + duration
    episodes["Gap"] = gap.values
    episodes["Gap[minutes]"] = (gap.dt.total_seconds() / 60).round(3).values

    episodes["Quantity"] = grouped["Quantity"].values

    # Rate = quantity / duration_minutes (NaN where duration is NaT)
    rate = grouped["Quantity"] / duration_minutes
    episodes["Rate"] = rate.values

    return episodes
