import pandas as pd


def filter_animals(df: pd.DataFrame, animal_ids: list[str]) -> pd.DataFrame:
    result = df[df["Animal"].isin(animal_ids)]
    result["Animal"] = result["Animal"].cat.remove_unused_categories()
    result.reset_index(drop=True, inplace=True)
    return result
