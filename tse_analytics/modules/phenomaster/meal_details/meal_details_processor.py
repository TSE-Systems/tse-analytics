import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings


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
        if "Drink1EpisodeId" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Drink1") + 1, "Drink1EpisodeId", None)
        else:
            meal_events_df["Drink1EpisodeId"] = None
        drink1_episode_number = 0
        drink1_episode_start = None
        drink1_episode_last_timestamp = None

    if feed1_present:
        if "Feed1EpisodeId" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Feed1") + 1, "Feed1EpisodeId", None)
        else:
            meal_events_df["Feed1EpisodeId"] = None
        feed1_episode_number = 0
        feed1_episode_start = None
        feed1_episode_last_timestamp = None

    if drink2_present:
        if "Drink2EpisodeId" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Drink2") + 1, "Drink2EpisodeId", None)
        else:
            meal_events_df["Drink2EpisodeId"] = None
        drink2_episode_number = 0
        drink2_episode_start = None
        drink2_episode_last_timestamp = None

    if feed2_present:
        if "Feed2EpisodeId" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Feed2") + 1, "Feed2EpisodeId", None)
        else:
            meal_events_df["Feed2EpisodeId"] = None
        feed2_episode_number = 0
        feed2_episode_start = None
        feed2_episode_last_timestamp = None

    for index, row in df.iterrows():
        timestamp = row["DateTime"]

        if drink1_present:
            if row["Drink1"] > 0:
                if drink1_episode_start is None:
                    if row["Drink1"] >= meal_details_settings.drinking_minimum_amount:
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
                    if row["Feed1"] >= meal_details_settings.feeding_minimum_amount:
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
                    if row["Drink2"] >= meal_details_settings.drinking_minimum_amount:
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
                    if row["Feed2"] >= meal_details_settings.feeding_minimum_amount:
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

    return meal_events_df


def __extract_sensor_episodes(animal_no: int, box_no: int, meal_events_df: pd.DataFrame, sensor: str) -> pd.DataFrame:
    id_ = []
    start_ = []
    duration_ = []
    offset_ = []
    gap_ = []
    quantity_ = []
    rate_ = []

    episode_ids = list(meal_events_df[f"{sensor}EpisodeId"].dropna().unique())
    for episode_id in episode_ids:
        df = meal_events_df[meal_events_df[f"{sensor}EpisodeId"] == episode_id]
        id_.append(episode_id)
        start_.append(df["DateTime"].iloc[0])
        quantity_.append(df[sensor].sum())

    result = pd.DataFrame.from_dict({
        "Sensor": sensor,
        "Animal": animal_no,
        "Box": box_no,
        "Id": id_,
        "Start": start_,
        "Quantity": quantity_,
    })
    return result


def __extract_meal_episodes(
    animal_no: int,
    box_no: int,
    meal_events_df: pd.DataFrame,
    drink1_present: bool,
    feed1_present: bool,
    drink2_present: bool,
    feed2_present: bool,
) -> pd.DataFrame:
    meal_episodes_df = None

    if drink1_present:
        drink1_episodes_df = __extract_sensor_episodes(animal_no, box_no, meal_events_df, "Drink1")
        if meal_episodes_df is None:
            meal_episodes_df = drink1_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, drink1_episodes_df], ignore_index=True)

    if feed1_present:
        feed1_episodes_df = __extract_sensor_episodes(animal_no, box_no, meal_events_df, "Feed1")
        if meal_episodes_df is None:
            meal_episodes_df = feed1_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, feed1_episodes_df], ignore_index=True)

    if drink2_present:
        drink2_episodes_df = __extract_sensor_episodes(animal_no, box_no, meal_events_df, "Drink2")
        if meal_episodes_df is None:
            meal_episodes_df = drink2_episodes_df
        else:
            meal_episodes_df = pd.concat([meal_episodes_df, drink2_episodes_df], ignore_index=True)

    if feed2_present:
        feed2_episodes_df = __extract_sensor_episodes(animal_no, box_no, meal_events_df, "Feed2")
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
) -> pd.DataFrame:
    drink1_present = "Drink1" in meal_details_df.columns
    feed1_present = "Feed1" in meal_details_df.columns
    drink2_present = "Drink2" in meal_details_df.columns
    feed2_present = "Feed2" in meal_details_df.columns

    meal_events_df = __extract_meal_events(
        meal_details_df, meal_details_settings, drink1_present, feed1_present, drink2_present, feed2_present
    )
    meal_episodes_df = __extract_meal_episodes(
        animal_number, box_number, meal_events_df, drink1_present, feed1_present, drink2_present, feed2_present
    )

    return meal_events_df, meal_episodes_df
