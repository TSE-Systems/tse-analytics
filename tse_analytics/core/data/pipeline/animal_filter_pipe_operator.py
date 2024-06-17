import pandas as pd

from tse_analytics.core.data.pipeline.pipe_operator import PipeOperator
from tse_analytics.core.data.shared import Animal


class AnimalFilterPipeOperator(PipeOperator):
    def __init__(self, animals: list[Animal]):
        self.animals = animals

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        animal_ids = [animal.id for animal in self.animals]
        result = df[df["Animal"].isin(animal_ids)]
        return result
