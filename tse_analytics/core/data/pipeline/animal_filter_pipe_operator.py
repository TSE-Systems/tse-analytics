import pandas as pd


def filter_animals(df: pd.DataFrame, animal_ids: list[str]) -> pd.DataFrame:
    return df[df["Animal"].isin(animal_ids)]
