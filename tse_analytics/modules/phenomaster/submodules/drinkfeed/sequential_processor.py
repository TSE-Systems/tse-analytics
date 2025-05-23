import pandas as pd

from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.drinkfeed_settings import DrinkFeedSettings


def _find_invalid_episodes(events_df: pd.DataFrame, sensor: str, minimum_amount: float):
    episode_id_column = f"{sensor}EpisodeId"
    episodes_ids = list(events_df[episode_id_column].unique())
    for episode_id in episodes_ids:
        episode_df = events_df[events_df[episode_id_column] == episode_id]
        if episode_df[sensor].sum() < minimum_amount:
            events_df.loc[events_df[episode_id_column] == episode_id, episode_id_column] = pd.NA

    return events_df


def _extract_events(
    df: pd.DataFrame,
    drinkfeed_settings: DrinkFeedSettings,
    drink1_present: bool,
    feed1_present: bool,
    drink2_present: bool,
    feed2_present: bool,
    drink_present: bool,
    feed_present: bool,
) -> pd.DataFrame:
    events_df = df.copy()
    timedelta = pd.Timedelta(
        hours=drinkfeed_settings.intermeal_interval.hour,
        minutes=drinkfeed_settings.intermeal_interval.minute,
        seconds=drinkfeed_settings.intermeal_interval.second,
    )

    if drink1_present:
        events_df.insert(events_df.columns.get_loc("Drink1") + 1, "Drink1EpisodeId", pd.NA)
        events_df["Drink1EpisodeId"] = events_df["Drink1EpisodeId"].astype("Int64")
        events_df.insert(events_df.columns.get_loc("Drink1") + 2, "Drink1Gap", pd.NA)
        drink1_episode_number = 0
        drink1_episode_start = None
        drink1_episode_last_timestamp = None

    if feed1_present:
        events_df.insert(events_df.columns.get_loc("Feed1") + 1, "Feed1EpisodeId", pd.NA)
        events_df["Feed1EpisodeId"] = events_df["Feed1EpisodeId"].astype("Int64")
        events_df.insert(events_df.columns.get_loc("Feed1") + 2, "Feed1Gap", pd.NA)
        feed1_episode_number = 0
        feed1_episode_start = None
        feed1_episode_last_timestamp = None

    if drink2_present:
        events_df.insert(events_df.columns.get_loc("Drink2") + 1, "Drink2EpisodeId", pd.NA)
        events_df["Drink2EpisodeId"] = events_df["Drink2EpisodeId"].astype("Int64")
        events_df.insert(events_df.columns.get_loc("Drink2") + 2, "Drink2Gap", pd.NA)
        drink2_episode_number = 0
        drink2_episode_start = None
        drink2_episode_last_timestamp = None

    if feed2_present:
        events_df.insert(events_df.columns.get_loc("Feed2") + 1, "Feed2EpisodeId", pd.NA)
        events_df["Feed2EpisodeId"] = events_df["Feed2EpisodeId"].astype("Int64")
        events_df.insert(events_df.columns.get_loc("Feed2") + 2, "Feed2Gap", pd.NA)
        feed2_episode_number = 0
        feed2_episode_start = None
        feed2_episode_last_timestamp = None

    if drink_present:
        events_df.insert(events_df.columns.get_loc("Drink") + 1, "DrinkEpisodeId", pd.NA)
        events_df["DrinkEpisodeId"] = events_df["DrinkEpisodeId"].astype("Int64")
        events_df.insert(events_df.columns.get_loc("Drink") + 2, "DrinkGap", pd.NA)
        drink_episode_number = 0
        drink_episode_start = None
        drink_episode_last_timestamp = None

    if feed_present:
        events_df.insert(events_df.columns.get_loc("Feed") + 1, "FeedEpisodeId", pd.NA)
        events_df["FeedEpisodeId"] = events_df["FeedEpisodeId"].astype("Int64")
        events_df.insert(events_df.columns.get_loc("Feed") + 2, "FeedGap", pd.NA)
        feed_episode_number = 0
        feed_episode_start = None
        feed_episode_last_timestamp = None

    for index, row in df.iterrows():
        timestamp = row["DateTime"]

        if drink1_present:
            if row["Drink1"] > 0:
                if drink1_episode_last_timestamp is None:
                    # First measurement
                    drink1_episode_start = timestamp
                    events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                    drink1_episode_last_timestamp = timestamp
                else:
                    if drink1_episode_start is None:
                        drink1_episode_start = timestamp
                        if timestamp - drink1_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                        else:
                            drink1_episode_number = drink1_episode_number + 1
                            events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                        events_df.at[index, "Drink1Gap"] = timestamp - drink1_episode_last_timestamp
                        drink1_episode_last_timestamp = timestamp
                    else:
                        if timestamp - drink1_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                            events_df.at[index, "Drink1Gap"] = timestamp - drink1_episode_last_timestamp
                            drink1_episode_last_timestamp = timestamp
                        else:
                            drink1_episode_number = drink1_episode_number + 1
                            events_df.at[index, "Drink1EpisodeId"] = drink1_episode_number
                            events_df.at[index, "Drink1Gap"] = timestamp - drink1_episode_last_timestamp
                            drink1_episode_start = None
                            drink1_episode_last_timestamp = timestamp

        if feed1_present:
            if row["Feed1"] > 0:
                if feed1_episode_last_timestamp is None:
                    # First measurement
                    feed1_episode_start = timestamp
                    events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                    feed1_episode_last_timestamp = timestamp
                else:
                    if feed1_episode_start is None:
                        feed1_episode_start = timestamp
                        if timestamp - feed1_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                        else:
                            feed1_episode_number = feed1_episode_number + 1
                            events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                        events_df.at[index, "Feed1Gap"] = timestamp - feed1_episode_last_timestamp
                        feed1_episode_last_timestamp = timestamp
                    else:
                        if timestamp - feed1_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                            events_df.at[index, "Feed1Gap"] = timestamp - feed1_episode_last_timestamp
                            feed1_episode_last_timestamp = timestamp
                        else:
                            feed1_episode_number = feed1_episode_number + 1
                            events_df.at[index, "Feed1EpisodeId"] = feed1_episode_number
                            events_df.at[index, "Feed1Gap"] = timestamp - feed1_episode_last_timestamp
                            feed1_episode_start = None
                            feed1_episode_last_timestamp = timestamp

        if drink2_present:
            if row["Drink2"] > 0:
                if drink2_episode_last_timestamp is None:
                    # First measurement
                    drink2_episode_start = timestamp
                    events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                    drink2_episode_last_timestamp = timestamp
                else:
                    if drink2_episode_start is None:
                        drink2_episode_start = timestamp
                        if timestamp - drink2_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                        else:
                            drink2_episode_number = drink2_episode_number + 1
                            events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                        events_df.at[index, "Drink2Gap"] = timestamp - drink2_episode_last_timestamp
                        drink2_episode_last_timestamp = timestamp
                    else:
                        if timestamp - drink2_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                            events_df.at[index, "Drink2Gap"] = timestamp - drink2_episode_last_timestamp
                            drink2_episode_last_timestamp = timestamp
                        else:
                            drink2_episode_number = drink2_episode_number + 1
                            events_df.at[index, "Drink2EpisodeId"] = drink2_episode_number
                            events_df.at[index, "Drink2Gap"] = timestamp - drink2_episode_last_timestamp
                            drink2_episode_start = None
                            drink2_episode_last_timestamp = timestamp

        if feed2_present:
            if row["Feed2"] > 0:
                if feed2_episode_last_timestamp is None:
                    # First measurement
                    feed2_episode_start = timestamp
                    events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                    feed2_episode_last_timestamp = timestamp
                else:
                    if feed2_episode_start is None:
                        feed2_episode_start = timestamp
                        if timestamp - feed2_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                        else:
                            feed2_episode_number = feed2_episode_number + 1
                            events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                        events_df.at[index, "Feed2Gap"] = timestamp - feed2_episode_last_timestamp
                        feed2_episode_last_timestamp = timestamp
                    else:
                        if timestamp - feed2_episode_last_timestamp <= timedelta:
                            events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                            events_df.at[index, "Feed2Gap"] = timestamp - feed2_episode_last_timestamp
                            feed2_episode_last_timestamp = timestamp
                        else:
                            feed2_episode_number = feed2_episode_number + 1
                            events_df.at[index, "Feed2EpisodeId"] = feed2_episode_number
                            events_df.at[index, "Feed2Gap"] = timestamp - feed2_episode_last_timestamp
                            feed2_episode_start = None
                            feed2_episode_last_timestamp = timestamp

        if drink_present:
            if row["Drink"] > 0:
                if drink_episode_last_timestamp is None:
                    # First measurement
                    drink_episode_start = timestamp
                    events_df.at[index, "DrinkEpisodeId"] = drink_episode_number
                    drink_episode_last_timestamp = timestamp
                else:
                    if drink_episode_start is None:
                        drink_episode_start = timestamp
                        if timestamp - drink_episode_last_timestamp <= timedelta:
                            events_df.at[index, "DrinkEpisodeId"] = drink_episode_number
                        else:
                            drink_episode_number = drink_episode_number + 1
                            events_df.at[index, "DrinkEpisodeId"] = drink_episode_number
                        events_df.at[index, "DrinkGap"] = timestamp - drink_episode_last_timestamp
                        drink_episode_last_timestamp = timestamp
                    else:
                        if timestamp - drink_episode_last_timestamp <= timedelta:
                            events_df.at[index, "DrinkEpisodeId"] = drink_episode_number
                            events_df.at[index, "DrinkGap"] = timestamp - drink_episode_last_timestamp
                            drink_episode_last_timestamp = timestamp
                        else:
                            drink_episode_number = drink_episode_number + 1
                            events_df.at[index, "DrinkEpisodeId"] = drink_episode_number
                            events_df.at[index, "DrinkGap"] = timestamp - drink_episode_last_timestamp
                            drink_episode_start = None
                            drink_episode_last_timestamp = timestamp

        if feed_present:
            if row["Feed"] > 0:
                if feed_episode_last_timestamp is None:
                    # First measurement
                    feed_episode_start = timestamp
                    events_df.at[index, "FeedEpisodeId"] = feed_episode_number
                    feed_episode_last_timestamp = timestamp
                else:
                    if feed_episode_start is None:
                        feed_episode_start = timestamp
                        if timestamp - feed_episode_last_timestamp <= timedelta:
                            events_df.at[index, "FeedEpisodeId"] = feed_episode_number
                        else:
                            feed_episode_number = feed_episode_number + 1
                            events_df.at[index, "FeedEpisodeId"] = feed_episode_number
                        events_df.at[index, "FeedGap"] = timestamp - feed_episode_last_timestamp
                        feed_episode_last_timestamp = timestamp
                    else:
                        if timestamp - feed_episode_last_timestamp <= timedelta:
                            events_df.at[index, "FeedEpisodeId"] = feed_episode_number
                            events_df.at[index, "FeedGap"] = timestamp - feed_episode_last_timestamp
                            feed_episode_last_timestamp = timestamp
                        else:
                            feed_episode_number = feed_episode_number + 1
                            events_df.at[index, "FeedEpisodeId"] = feed_episode_number
                            events_df.at[index, "FeedGap"] = timestamp - feed_episode_last_timestamp
                            feed_episode_start = None
                            feed_episode_last_timestamp = timestamp

    if drink1_present:
        events_df = _find_invalid_episodes(events_df, "Drink1", drinkfeed_settings.drinking_minimum_amount)
    if feed1_present:
        events_df = _find_invalid_episodes(events_df, "Feed1", drinkfeed_settings.feeding_minimum_amount)

    if drink2_present:
        events_df = _find_invalid_episodes(events_df, "Drink2", drinkfeed_settings.drinking_minimum_amount)
    if feed2_present:
        events_df = _find_invalid_episodes(events_df, "Feed2", drinkfeed_settings.feeding_minimum_amount)

    if drink_present:
        events_df = _find_invalid_episodes(events_df, "Drink", drinkfeed_settings.drinking_minimum_amount)
    if feed_present:
        events_df = _find_invalid_episodes(events_df, "Feed", drinkfeed_settings.feeding_minimum_amount)

    return events_df


def _extract_sensor_episodes(
    animal_no: int, box_no: int, start_timestamp: pd.Timestamp, events_df: pd.DataFrame, sensor: str
) -> pd.DataFrame:
    id_ = []
    start_ = []
    duration_ = []
    duration_minutes_ = []
    offset_ = []
    offset_minutes_ = []
    quantity_ = []
    rate_ = []

    episode_ids = list(events_df[f"{sensor}EpisodeId"].dropna().unique())
    for episode_id in episode_ids:
        df = events_df[events_df[f"{sensor}EpisodeId"] == episode_id]
        id_.append(episode_id)
        start_.append(df["DateTime"].iloc[0])
        offset_delta = df["DateTime"].iloc[0] - start_timestamp
        offset_.append(offset_delta)
        offset_minutes_.append(round(offset_delta.total_seconds() / 60, 3))

        quantity = df[sensor].sum()
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
        "Animal": animal_no,
        "Box": box_no,
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


def _extract_episodes(
    animal_no: int,
    box_no: int,
    start_timestamp: pd.Timestamp,
    events_df: pd.DataFrame,
    drink1_present: bool,
    feed1_present: bool,
    drink2_present: bool,
    feed2_present: bool,
    drink_present: bool,
    feed_present: bool,
) -> pd.DataFrame:
    episodes_df = None

    if drink1_present:
        drink1_episodes_df = _extract_sensor_episodes(animal_no, box_no, start_timestamp, events_df, "Drink1")
        if episodes_df is None:
            episodes_df = drink1_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, drink1_episodes_df], ignore_index=True)

    if feed1_present:
        feed1_episodes_df = _extract_sensor_episodes(animal_no, box_no, start_timestamp, events_df, "Feed1")
        if episodes_df is None:
            episodes_df = feed1_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, feed1_episodes_df], ignore_index=True)

    if drink2_present:
        drink2_episodes_df = _extract_sensor_episodes(animal_no, box_no, start_timestamp, events_df, "Drink2")
        if episodes_df is None:
            episodes_df = drink2_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, drink2_episodes_df], ignore_index=True)

    if feed2_present:
        feed2_episodes_df = _extract_sensor_episodes(animal_no, box_no, start_timestamp, events_df, "Feed2")
        if episodes_df is None:
            episodes_df = feed2_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, feed2_episodes_df], ignore_index=True)

    if drink_present:
        drink_episodes_df = _extract_sensor_episodes(animal_no, box_no, start_timestamp, events_df, "Drink")
        if episodes_df is None:
            episodes_df = drink_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, drink_episodes_df], ignore_index=True)

    if feed_present:
        feed_episodes_df = _extract_sensor_episodes(animal_no, box_no, start_timestamp, events_df, "Feed")
        if episodes_df is None:
            episodes_df = feed_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, feed_episodes_df], ignore_index=True)

    return episodes_df


def _process_box(
    box_number: int,
    animal_number: int,
    drinkfeed_df: pd.DataFrame,
    drinkfeed_settings: DrinkFeedSettings,
    start_timestamp: pd.Timestamp,
):
    drink1_present = "Drink1" in drinkfeed_df.columns
    feed1_present = "Feed1" in drinkfeed_df.columns
    drink2_present = "Drink2" in drinkfeed_df.columns
    feed2_present = "Feed2" in drinkfeed_df.columns
    drink_present = "Drink" in drinkfeed_df.columns and (not drink1_present and not drink2_present)
    feed_present = "Feed" in drinkfeed_df.columns and (not feed1_present and not feed2_present)

    events_df = _extract_events(
        drinkfeed_df,
        drinkfeed_settings,
        drink1_present,
        feed1_present,
        drink2_present,
        feed2_present,
        drink_present,
        feed_present,
    )

    episodes_df = _extract_episodes(
        animal_number,
        box_number,
        start_timestamp,
        events_df,
        drink1_present,
        feed1_present,
        drink2_present,
        feed2_present,
        drink_present,
        feed_present,
    )

    return events_df, episodes_df


def process_drinkfeed_sequences(
    drinkfeed_data: DrinkFeedData, drinkfeed_settings: DrinkFeedSettings, diets_dict: dict[str, float]
):
    box_to_animal_map = {}
    for animal in drinkfeed_data.dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

    all_box_numbers = list(drinkfeed_data.raw_df["Box"].unique())

    events_df = None
    episodes_df = None

    for box_number in all_box_numbers:
        df = drinkfeed_data.raw_df[drinkfeed_data.raw_df["Box"] == box_number]

        box_events_df, box_episodes_df = _process_box(
            box_number,
            box_to_animal_map[box_number],
            df,
            drinkfeed_settings,
            drinkfeed_data.raw_df["DateTime"].iloc[0],
        )

        if events_df is None:
            events_df = box_events_df
        else:
            events_df = pd.concat([events_df, box_events_df], ignore_index=True)

        if episodes_df is None:
            episodes_df = box_episodes_df
        else:
            episodes_df = pd.concat([episodes_df, box_episodes_df], ignore_index=True)

    # Add caloric value column
    episodes_df.insert(episodes_df.columns.get_loc("Quantity") + 1, "Quantity-kcal", episodes_df["Box"].astype(int))
    episodes_df = episodes_df.replace({"Quantity-kcal": diets_dict})
    episodes_df["Quantity-kcal"] = episodes_df["Quantity-kcal"] * episodes_df["Quantity"]

    # convert types
    episodes_df = episodes_df.astype({
        "Sensor": "category",
        "Animal": "category",
        "Box": int,
        "Id": int,
        "Duration": "timedelta64[ns]",
        "Gap": "timedelta64[ns]",
        "Rate": "float64",
    })

    return events_df, episodes_df
