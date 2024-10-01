import pandas as pd

from tse_analytics.core.data.shared import Animal


def filter_animals(df: pd.DataFrame, animals: dict[str, Animal]) -> pd.DataFrame:
    enabled_animal_ids = [animal.id for animal in animals.values() if animal.enabled]
    if len(enabled_animal_ids) == len(animals):
        return df

    result = df[df["Animal"].isin(enabled_animal_ids)]
    result["Animal"] = result["Animal"].cat.remove_unused_categories()
    result.reset_index(drop=True, inplace=True)
    return result
