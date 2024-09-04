import pandas as pd

from tse_analytics.core.data.shared import Animal


def filter_animals(df: pd.DataFrame, animals: list[Animal]) -> pd.DataFrame:
    animal_ids = [animal.id for animal in animals]
    result = df[df["Animal"].isin(animal_ids)]
    return result
