import pandas as pd

from tse_analytics.modules.phenomaster.meal_details.meal_details_settings import MealDetailsSettings


def process_box(box_number: int, df: pd.DataFrame, meal_details_settings: MealDetailsSettings) -> pd.DataFrame:
    meal_events_df = df.copy()
    timedelta = pd.Timedelta(
        hours=meal_details_settings.intermeal_interval.hour,
        minutes=meal_details_settings.intermeal_interval.minute,
        seconds=meal_details_settings.intermeal_interval.second,
    )

    drink1_present = "Drink1" in meal_events_df.columns
    if drink1_present:
        if "Drink1EpisodeNo" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Drink1") + 1, "Drink1EpisodeNo", None)
        else:
            meal_events_df["Drink1EpisodeNo"] = None
        drink1_episode_number = 0
        drink1_episode_start = None
        drink1_episode_last_timestamp = None

    feed1_present = "Feed1" in meal_events_df.columns
    if feed1_present:
        if "Feed1EpisodeNo" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Feed1") + 1, "Feed1EpisodeNo", None)
        else:
            meal_events_df["Feed1EpisodeNo"] = None
        feed1_episode_number = 0
        feed1_episode_start = None
        feed1_episode_last_timestamp = None

    drink2_present = "Drink2" in meal_events_df.columns
    if drink2_present:
        if "Drink2EpisodeNo" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Drink2") + 1, "Drink2EpisodeNo", None)
        else:
            meal_events_df["Drink2EpisodeNo"] = None
        drink2_episode_number = 0
        drink2_episode_start = None
        drink2_episode_last_timestamp = None

    feed2_present = "Feed2" in meal_events_df.columns
    if feed2_present:
        if "Feed2EpisodeNo" not in meal_events_df.columns:
            meal_events_df.insert(meal_events_df.columns.get_loc("Feed2") + 1, "Feed2EpisodeNo", None)
        else:
            meal_events_df["Feed2EpisodeNo"] = None
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
                        meal_events_df.at[index, "Drink1EpisodeNo"] = drink1_episode_number
                        drink1_episode_last_timestamp = timestamp
                else:
                    if timestamp - drink1_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Drink1EpisodeNo"] = drink1_episode_number
                        drink1_episode_last_timestamp = timestamp
                    else:
                        drink1_episode_number = drink1_episode_number + 1
                        meal_events_df.at[index, "Drink1EpisodeNo"] = drink1_episode_number
                        drink1_episode_start = None
                        drink1_episode_last_timestamp = None

        if feed1_present:
            if row["Feed1"] > 0:
                if feed1_episode_start is None:
                    if row["Feed1"] >= meal_details_settings.feeding_minimum_amount:
                        feed1_episode_start = timestamp
                        meal_events_df.at[index, "Feed1EpisodeNo"] = feed1_episode_number
                        feed1_episode_last_timestamp = timestamp
                else:
                    if timestamp - feed1_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Feed1EpisodeNo"] = feed1_episode_number
                        feed1_episode_last_timestamp = timestamp
                    else:
                        feed1_episode_number = feed1_episode_number + 1
                        meal_events_df.at[index, "Feed1EpisodeNo"] = feed1_episode_number
                        feed1_episode_start = None
                        feed1_episode_last_timestamp = None

        if drink2_present:
            if row["Drink2"] > 0:
                if drink2_episode_start is None:
                    if row["Drink2"] >= meal_details_settings.drinking_minimum_amount:
                        drink2_episode_start = timestamp
                        meal_events_df.at[index, "Drink2EpisodeNo"] = drink2_episode_number
                        drink2_episode_last_timestamp = timestamp
                else:
                    if timestamp - drink2_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Drink2EpisodeNo"] = drink2_episode_number
                        drink2_episode_last_timestamp = timestamp
                    else:
                        drink2_episode_number = drink2_episode_number + 1
                        meal_events_df.at[index, "Drink2EpisodeNo"] = drink2_episode_number
                        drink2_episode_start = None
                        drink2_episode_last_timestamp = None

        if feed2_present:
            if row["Feed2"] > 0:
                if feed2_episode_start is None:
                    if row["Feed2"] >= meal_details_settings.feeding_minimum_amount:
                        feed2_episode_start = timestamp
                        meal_events_df.at[index, "Feed2EpisodeNo"] = feed2_episode_number
                        feed2_episode_last_timestamp = timestamp
                else:
                    if timestamp - feed2_episode_last_timestamp <= timedelta:
                        meal_events_df.at[index, "Feed2EpisodeNo"] = feed2_episode_number
                        feed2_episode_last_timestamp = timestamp
                    else:
                        feed2_episode_number = feed2_episode_number + 1
                        meal_events_df.at[index, "Feed2EpisodeNo"] = feed2_episode_number
                        feed2_episode_start = None
                        feed2_episode_last_timestamp = None

    return meal_events_df
