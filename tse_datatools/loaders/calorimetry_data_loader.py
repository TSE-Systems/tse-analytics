import pandas as pd


class CalorimetryDataLoader:

    @staticmethod
    def load(path: str) -> pd.DataFrame:
        df = pd.read_csv(path, delimiter="\t")
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        return df
