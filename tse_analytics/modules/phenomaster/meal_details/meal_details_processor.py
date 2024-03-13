import numpy as np
import pandas as pd

from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings


def __find_invalid_episodes(meal_events_df: pd.DataFrame, sensor: str, minimum_amount: float):
    episode_id_column = f"{sensor}EpisodeId"
    episodes_ids = list(meal_events_df[episode_id_column].unique())
    for episode_id in episodes_ids:
        episode_df = meal_events_df[meal_events_df[episode_id_column] == episode_id]
        if episode_df[sensor].sum() < minimum_amount:
            meal_events_df.loc[meal_events_df[episode_id_column] == episode_id, episode_id_column] = pd.NA

    return meal_events_df


def __extract_meal_events(
    df: pd.DataFrame,
    meal_details_settings: MealDetailsSettings,
    drink1_present: bool,
    feed1_present: bool,
    drink2_present: bool,
    feed2_present: bool,
) -> pd.DataFrame:
    meal_events_df = df.copy()
    timedelta = pd.Timedelta(
        hours=meal_details_settings.intermeal_interval.hour,
        minutes=meal_details_settings.intermeal_interval.minute,
        seconds=meal_details_settings.intermeal_interval.second,
    )

    if drink1_present:
        meal_events_df.insert(meal_events_df.columns.get_loc("Drink1") + 1, "Drink1EpisodeId", pd.NA)
        meal_events_df["Drink1EpisodeId"] = meal_events_df["Drink1EpisodeId"].astype("Int64")
        drink1_episode_number = 0
        drink1_episode_start = None
        drink1_episode_last_timestamp = None

    if feed1_present:
        meal_events_df.insert(meal_events_df.columns.get_loc("Feed1") + 1, "Feed1EpisodeId", pd.NA)
        meal_events_df["Feed1EpisodeId"] = meal_events_df["Feed1EpisodeId"].astype("Int64")
        feed1_episode_number = 0
        feed1_episode_start = None
        feed1_episode_last_timestamp = None

    if drink2_present:
        meal_events_df.insert(meal_events_df.columns.get_loc("Drink2") + 1, "Drink2EpisodeId", pd.NA)
        meal_events_df["Drink2EpisodeId"] = meal_events_df["Drink2EpisodeId"].astype("Int64")
        drink2_episode_number = 0
        drink2_episode_start = None
        drink2_episode_last_timestamp = None

    if feed2_present:
        meal_events_df.insert(meal_events_df.columns.get_loc("Feed2") + 1, "Feed2EpisodeId", pd.NA)
        meal_events_df["Feed2EpisodeId"] = meal_events_df["Feed2EpisodeId"].astype("Int64")
        feed2_episode_number = 0
        feed2_episode_start = None
        feed2_episode_last_timestamp = None

    for index, row in df.iterrows():
        timestamp = row["DateTime"]

        if drink1_present:
            if row["Drink1"] > 0:
                if drink1_episode_start is None:
                    drink1_episode_start = timestamp
                    meal_events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                    drink1_episode_last_timestamp = timestamp
                else:
                    if timestamp - drink1_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                        drink1_episode_last_timestamp = timestamp
                    else:
                        drink1_episode_number = drink1_episode_number + 1
                        meal_events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                        drink1_episode_start = None
                        drink1_episode_last_timestamp = None

        if feed1_present:
            if row["Feed1"] > 0:
                if feed1_episode_start is None:
                    feed1_episode_start = timestamp
                    meal_events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                    feed1_episode_last_timestamp = timestamp
                else:
                    if timestamp - feed1_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                        feed1_episode_last_timestamp = timestamp
                    else:
                        feed1_episode_number = feed1_episode_number + 1
                        meal_events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                        feed1_episode_start = None
                        feed1_episode_last_timestamp = None

        if drink2_present:
            if row["Drink2"] > 0:
                if drink2_episode_start is None:
                    drink2_episode_start = timestamp
                    meal_events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                    drink2_episode_last_timestamp = timestamp
                else:
                    if timestamp - drink2_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                        drink2_episode_last_timestamp = timestamp
                    else:
                        drink2_episode_number = drink2_episode_number + 1
                        meal_events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                        drink2_episode_start = None
                        drink2_episode_last_timestamp = None

        if feed2_present:
            if row["Feed2"] > 0:
                if feed2_episode_start is None:
                    feed2_episode_start = timestamp
                    meal_events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                    feed2_episode_last_timestamp = timestamp
                else:
                    if timestamp - feed2_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                        feed2_episode_last_timestamp = timestamp
                    else:
                        feed2_episode_number = feed2_episode_number + 1
                        meal_events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                        feed2_episode_start = None
                        feed2_episode_last_timestamp = None

    if drink1_present:
        meal_events_df = __find_invalid_episodes(
            meal_events_df, "Drink1", meal_details_settings.drinking_minimum_amount
        )
    if feed1_present:
        meal_events_df = __find_invalid_episodes(meal_events_df, "Feed1", meal_details_settings.feeding_minimum_amount)

    if drink2_present:
        meal_events_df = __find_invalid_episodes(
            meal_events_df, "Drink2", meal_details_settings.drinking_minimum_amount
        )
    if feed2_present:
        meal_events_df = __find_invalid_episodes(meal_events_df, "Feed2", meal_details_settings.feeding_minimum_amount)

    return meal_events_df


def __extract_sensor_episodes(
    animal_no: int, box_no: int, start_timestamp: pd.Timestamp, meal_events_df: pd.DataFrame, sensor: str
) -> pd.DataFrame:
    id_ = []
    start_ = []
    duration_ = []
    offset_ = []
    quantity_ = []
    rate_ = []

    episode_ids = list(meal_events_df[f"{sensor}EpisodeId"].dropna().unique())
    for episode_id in episode_ids:
        df = meal_events_df[meal_events_df[f"{sensor}EpisodeId"] == episode_id]
        id_.append(episode_id)
        start_.append(df["DateTime"].iloc[0])
        offset_.append(df["DateTime"].iloc[0] - start_timestamp)

        quantity = df[sensor].sum()
        quantity_.append(quantity)

        if len(df["DateTime"]) > 1:
            duration = df["DateTime"].iloc[-1] - df["DateTime"].iloc[0]
            duration_.append(duration)
            rate_.append(quantity / (duration.total_seconds() / 60))
        else:
            duration_.append(None)
            rate_.append(None)

    sensor_episodes_df = pd.DataFrame.from_dict({
        "Sensor": sensor,
        "Animal": animal_no,
        "Box": box_no,
        "Id": id_,
        "Start": start_,
        "Offset": offset_,
        "Duration": duration_,
        "Gap": None,
        "Quantity": quantity_,
        "Rate": rate_,
    })

    # Find gaps between episodes
    for index, episode_id in enumerate(episode_ids):
        if index < len(episode_ids) - 1:
            current_episode = sensor_episodes_df[sensor_episodes_df["Id"] == episode_id]
            next_episode = sensor_episodes_df[sensor_episodes_df["Id"] == episode_ids[index + 1]]
            sensor_episodes_df.loc[sensor_episodes_df["Id"] == episode_id, "Gap"] = (
                next_episode["Start"].iloc[0] - current_episode["Start"].iloc[0] + current_episode["Duration"].iloc[0]
            )

    return sensor_episodes_df


def __extract_meal_episodes(
    animal_no: int,
    box_no: int,
    start_timestamp: pd.Timestamp,
    meal_events_df: pd.DataFrame,
    drink1_present: bool,
    feed1_present: bool,
    drink2_present: bool,
    feed2_present: bool,
) -> pd.DataFrame:
    meal_episodes_df = None

    if drink1_present:
        drink1_episodes_df = __extract_sensor_episodes(animal_no, box_no, start_timestamp, meal_events_df, "Drink1")
        if meal_episodes_df is None:
            meal_episodes_df = drink1_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, drink1_episodes_df], ignore_index=True)

    if feed1_present:
        feed1_episodes_df = __extract_sensor_episodes(animal_no, box_no, start_timestamp, meal_events_df, "Feed1")
        if meal_episodes_df is None:
            meal_episodes_df = feed1_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, feed1_episodes_df], ignore_index=True)

    if drink2_present:
        drink2_episodes_df = __extract_sensor_episodes(animal_no, box_no, start_timestamp, meal_events_df, "Drink2")
        if meal_episodes_df is None:
            meal_episodes_df = drink2_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, drink2_episodes_df], ignore_index=True)

    if feed2_present:
        feed2_episodes_df = __extract_sensor_episodes(animal_no, box_no, start_timestamp, meal_events_df, "Feed2")
        if meal_episodes_df is None:
            meal_episodes_df = feed2_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, feed2_episodes_df], ignore_index=True)

    return meal_episodes_df


def process_box(
    box_number: int,
    animal_number: int,
    meal_details_df: pd.DataFrame,
    meal_details_settings: MealDetailsSettings,
    start_timestamp: pd.Timestamp,
):
    drink1_present = "Drink1" in meal_details_df.columns
    feed1_present = "Feed1" in meal_details_df.columns
    drink2_present = "Drink2" in meal_details_df.columns
    feed2_present = "Feed2" in meal_details_df.columns

    meal_events_df = __extract_meal_events(
        meal_details_df, meal_details_settings, drink1_present, feed1_present, drink2_present, feed2_present
    )

    meal_episodes_df = __extract_meal_episodes(
        animal_number,
        box_number,
        start_timestamp,
        meal_events_df,
        drink1_present,
        feed1_present,
        drink2_present,
        feed2_present,
    )

    return meal_events_df, meal_episodes_df


def process_meal_details(meal_details: MealDetails, meal_details_settings: MealDetailsSettings):
    box_to_animal_map = {}
    for animal in meal_details.dataset.animals.values():
        box_to_animal_map[animal.box] = animal.id

    all_box_numbers = list(meal_details.raw_df["Box"].unique())

    events_df = None
    episodes_df = None

    for box_number in all_box_numbers:
        df = meal_details.raw_df[meal_details.raw_df["Box"] == box_number]

        meal_events_df, meal_episodes_df = process_box(
            box_number,
            box_to_animal_map[box_number],
            df,
            meal_details_settings,
            meal_details.raw_df["DateTime"].iloc[0],
        )

        if events_df is None:
            events_df = meal_events_df
        else:
            events_df = pd.concat([events_df, meal_events_df], ignore_index=True)

        if episodes_df is None:
            episodes_df = meal_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, meal_episodes_df], ignore_index=True)

    # convert types
    episodes_df = episodes_df.astype({
        "Sensor": "category",
        "Animal": "category",
        "Box": "category",
        "Id": int,
        "Duration": "timedelta64[ns]",
        "Gap": "timedelta64[ns]",
        "Rate": "Float64",
    })

    return events_df, episodes_df
