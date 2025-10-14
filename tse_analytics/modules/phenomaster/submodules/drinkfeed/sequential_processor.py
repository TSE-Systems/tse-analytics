import pandas as pd

from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_bin_data import DrinkFeedBinData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings


def _find_invalid_episodes(events_df: pd.DataFrame, minimum_amount: float):
    episodes_ids = events_df["EpisodeId"].unique().tolist()
    for episode_id in episodes_ids:
        episode_df = events_df[events_df["EpisodeId"] == episode_id]
        if episode_df["Value"].sum() < minimum_amount:
            events_df.loc[events_df["EpisodeId"] == episode_id, "EpisodeId"] = pd.NA

    return events_df


def process_drinkfeed_sequences(
    drinkfeed_data: DrinkFeedBinData,
    long_df: pd.DataFrame,
    settings: DrinkFeedSettings,
    diets_dict: dict[str, float],
):
    # TODO: drop unnecessary rows
    long_df = long_df.loc[~(long_df["Value"] == 0)]

    long_df.sort_values(by=["DateTime"], inplace=True)
    long_df.reset_index(drop=True, inplace=True)

    sensors = long_df["Sensor"].unique().tolist()

    events_df = pd.DataFrame()
    episodes_df = pd.DataFrame()
    for animal_id in drinkfeed_data.dataset.animals.keys():
        animal_df = long_df[long_df["Animal"] == animal_id]
        animal_events_df, animal_episodes_df = _process_animal(
            animal_id,
            animal_df,
            sensors,
            settings,
            drinkfeed_data.raw_df["DateTime"].iloc[0],
        )
        events_df = pd.concat([events_df, animal_events_df], ignore_index=True)
        episodes_df = pd.concat([episodes_df, animal_episodes_df], ignore_index=True)

    # Add caloric value column
    episodes_df.insert(episodes_df.columns.get_loc("Quantity") + 1, "Quantity-kcal", episodes_df["Animal"])
    episodes_df = episodes_df.replace({"Quantity-kcal": diets_dict})
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
):
    animal_events_df = pd.DataFrame()
    animal_episodes_df = pd.DataFrame()
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
        animal_events_df = pd.concat([animal_events_df, sensor_events_df], ignore_index=True)

        sensor_episodes_df = _extract_sensor_episodes(
            animal_id,
            start_timestamp,
            sensor_events_df,
            sensor,
        )
        animal_episodes_df = pd.concat([animal_episodes_df, sensor_episodes_df], ignore_index=True)

    return animal_events_df, animal_episodes_df


def _extract_sensor_events(
    df: pd.DataFrame,
    sensor: str,
    settings: DrinkFeedSettings,
) -> pd.DataFrame:
    events_df = df.copy()

    timedelta = pd.Timedelta(
        hours=settings.intermeal_interval.hour,
        minutes=settings.intermeal_interval.minute,
        seconds=settings.intermeal_interval.second,
    )

    events_df.insert(1, "EpisodeId", pd.NA)
    events_df["EpisodeId"] = events_df["EpisodeId"].astype("Int64")
    events_df.insert(2, "Gap", pd.NA)

    episode_number = 0
    episode_start = None
    episode_last_timestamp = None

    for index, row in events_df.iterrows():
        timestamp = row["DateTime"]

        if episode_last_timestamp is None:
            # First measurement
            episode_start = timestamp
            events_df.at[index, "EpisodeId"] = episode_number
            episode_last_timestamp = timestamp
        else:
            if episode_start is None:
                episode_start = timestamp
                if timestamp - episode_last_timestamp <= timedelta:
                    events_df.at[index, "EpisodeId"] = episode_number
                else:
                    episode_number = episode_number + 1
                    events_df.at[index, "EpisodeId"] = episode_number
                events_df.at[index, "Gap"] = timestamp - episode_last_timestamp
                episode_last_timestamp = timestamp
            else:
                if timestamp - episode_last_timestamp <= timedelta:
                    events_df.at[index, "EpisodeId"] = episode_number
                    events_df.at[index, "Gap"] = timestamp - episode_last_timestamp
                    episode_last_timestamp = timestamp
                else:
                    episode_number = episode_number + 1
                    events_df.at[index, "EpisodeId"] = episode_number
                    events_df.at[index, "Gap"] = timestamp - episode_last_timestamp
                    episode_start = None
                    episode_last_timestamp = timestamp

    events_df = _find_invalid_episodes(events_df, settings.drinking_minimum_amount)

    return events_df


def _extract_sensor_episodes(
    animal_id: str,
    start_timestamp: pd.Timestamp,
    events_df: pd.DataFrame,
    sensor: str,
) -> pd.DataFrame:
    id_ = []
    start_ = []
    duration_ = []
    duration_minutes_ = []
    offset_ = []
    offset_minutes_ = []
    quantity_ = []
    rate_ = []

    episode_ids = events_df["EpisodeId"].dropna().unique().tolist()
    for episode_id in episode_ids:
        df = events_df[events_df["EpisodeId"] == episode_id]
        id_.append(episode_id)
        start_.append(df["DateTime"].iloc[0])
        offset_delta = df["DateTime"].iloc[0] - start_timestamp
        offset_.append(offset_delta)
        offset_minutes_.append(round(offset_delta.total_seconds() / 60, 3))

        quantity = df["Value"].sum()
        quantity_.append(quantity)

        if len(df["DateTime"]) > 1:
            duration = df["DateTime"].iloc[-1] - df["DateTime"].iloc[0]
            duration_.append(duration)
            duration_minutes = round(duration.total_seconds() / 60, 3)
            duration_minutes_.append(duration_minutes)
            rate_.append(quantity / duration_minutes)
        else:
            duration_.append(None)
            duration_minutes_.append(None)
            rate_.append(None)

    sensor_episodes_df = pd.DataFrame.from_dict({
        "Sensor": sensor,
        "Animal": animal_id,
        "Id": id_,
        "Start": start_,
        "Offset": offset_,
        "Offset[minutes]": offset_minutes_,
        "Duration": duration_,
        "Duration[minutes]": duration_minutes_,
        "Gap": pd.NA,
        "Gap[minutes]": pd.NA,
        "Quantity": quantity_,
        "Rate": rate_,
    })

    # Find gaps between episodes
    for index, episode_id in enumerate(episode_ids):
        if index < len(episode_ids) - 1:
            current_episode = sensor_episodes_df[sensor_episodes_df["Id"] == episode_id]
            next_episode = sensor_episodes_df[sensor_episodes_df["Id"] == episode_ids[index + 1]]
            gap = next_episode["Start"].iloc[0] - current_episode["Start"].iloc[0] + current_episode["Duration"].iloc[0]
            sensor_episodes_df.loc[sensor_episodes_df["Id"] == episode_id, "Gap"] = gap
            sensor_episodes_df.loc[sensor_episodes_df["Id"] == episode_id, "Gap[minutes]"] = round(
                gap.total_seconds() / 60, 3
            )

    return sensor_episodes_df
