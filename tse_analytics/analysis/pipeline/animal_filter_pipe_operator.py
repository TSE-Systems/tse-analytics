import pandas as pd

from tse_analytics.analysis.pipeline.pipe_operator import PipeOperator
from tse_analytics.data.animal import Animal


class AnimalFilterPipeOperator(PipeOperator):
    def __init__(self, selected_animals: list[Animal]):
        self.selected_animals = selected_animals

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        animal_ids = [animal.id for animal in self.selected_animals]
        result = df[df["Animal"].isin(animal_ids)]
        return result
