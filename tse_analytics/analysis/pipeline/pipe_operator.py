from abc import ABC, abstractmethod

import pandas as pd


class PipeOperator(ABC):
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
