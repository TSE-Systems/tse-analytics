import polars as pl

from tse_analytics.core.data.shared import Animal


def filter_animals(df: pl.DataFrame, animals: list[Animal]) -> pl.DataFrame:
    animal_ids = [animal.id for animal in animals]
    result = df.filter(pl.col("Animal").is_in(animal_ids))
    return result
