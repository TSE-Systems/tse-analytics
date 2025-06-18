"""
Pipeline operator for filtering animals in a DataFrame.

This module provides a function for filtering a DataFrame to include only
enabled animals.
"""

import pandas as pd

from tse_analytics.core.data.shared import Animal


def filter_animals(df: pd.DataFrame, animals: dict[str, Animal]) -> pd.DataFrame:
    """
    Filter a DataFrame to include only enabled animals.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter.
    animals : dict[str, Animal]
        Dictionary mapping animal IDs to Animal objects.

    Returns
    -------
    pd.DataFrame
        A filtered DataFrame containing only enabled animals.
    """
    enabled_animal_ids = [animal.id for animal in animals.values() if animal.enabled]
    if len(enabled_animal_ids) == len(animals):
        return df

    result = df[df["Animal"].isin(enabled_animal_ids)]
    result["Animal"] = result["Animal"].cat.remove_unused_categories()
    result.reset_index(drop=True, inplace=True)
    return result
