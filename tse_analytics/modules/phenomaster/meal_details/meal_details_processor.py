import pandas as pd

from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings


def process_box(box_number: int, df: pd.DataFrame, meal_details_settings: MealDetailsSettings) -> pd.DataFrame:
    result = df.copy()
    timedelta = pd.Timedelta(
        hours=meal_details_settings.intermeal_interval.hour,
        minutes=meal_details_settings.intermeal_interval.minute,
        seconds=meal_details_settings.intermeal_interval.second,
    )

    drink1_present = "Drink1" in result.columns
    if drink1_present:
        result.insert(result.columns.get_loc("Drink1") + 1, "Drink1EpisodeNo", None)
        drink1_episode_number = 0
        drink1_episode_start = None
        drink1_episode_last_timestamp = None

    feed1_present = "Feed1" in result.columns
    if feed1_present:
        result.insert(result.columns.get_loc("Feed1") + 1, "Feed1EpisodeNo", None)
        feed1_episode_number = 0
        feed1_episode_start = None
        feed1_episode_last_timestamp = None

    for index, row in df.iterrows():
        timestamp = row["DateTime"]

        if drink1_present:
            if row["Drink1"] > 0:
                if drink1_episode_start is None:
                    if row["Drink1"] >= meal_details_settings.drinking_minimum_amount:
                        drink1_episode_start = timestamp
                        result.at[index, "Drink1EpisodeNo"] = drink1_episode_number
                        drink1_episode_last_timestamp = timestamp
                else:
                    if timestamp - drink1_episode_last_timestamp <= timedelta:
                        result.at[index, "Drink1EpisodeNo"] = drink1_episode_number
                        drink1_episode_last_timestamp = timestamp
                    else:
                        drink1_episode_number = drink1_episode_number + 1
                        result.at[index, "Drink1EpisodeNo"] = drink1_episode_number
                        drink1_episode_start = None
                        drink1_episode_last_timestamp = None

        if feed1_present:
            if row["Feed1"] > 0:
                if feed1_episode_start is None:
                    if row["Feed1"] >= meal_details_settings.feeding_minimum_amount:
                        feed1_episode_start = timestamp
                        result.at[index, "Feed1EpisodeNo"] = feed1_episode_number
                        feed1_episode_last_timestamp = timestamp
                else:
                    if timestamp - feed1_episode_last_timestamp <= timedelta:
                        result.at[index, "Feed1EpisodeNo"] = feed1_episode_number
                        feed1_episode_last_timestamp = timestamp
                    else:
                        feed1_episode_number = feed1_episode_number + 1
                        result.at[index, "Feed1EpisodeNo"] = feed1_episode_number
                        feed1_episode_start = None
                        feed1_episode_last_timestamp = None

    return result
