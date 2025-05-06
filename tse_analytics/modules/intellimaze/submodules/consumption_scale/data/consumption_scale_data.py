import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-CS"


class ConsumptionScaleData:
    def __init__(
        self,
        dataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data

        self.device_ids = dataset.devices["ConsumptionScale"]
        self.device_ids.sort()

    def get_raw_data(self):
        return self.raw_data

    def get_device_ids(self):
        return self.device_ids

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.raw_data["Consumption"].copy()

        # Convert cumulative values to differential ones
        preprocessed_device_df = []
        device_ids = df["DeviceId"].unique().tolist()
        for i, device_id in enumerate(device_ids):
            device_data = df[df["DeviceId"] == device_id]
            device_data["Consumption"] = device_data["Consumption"].diff().fillna(df["Consumption"]).round(5)
            preprocessed_device_df.append(device_data)
        df = pd.concat(preprocessed_device_df, ignore_index=True, sort=False)

        tag_to_animal_map = {}
        for animal in self.dataset.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id

        # Replace animal tags with animal IDs
        df["Tag"] = df["Tag"].replace(tag_to_animal_map)

        df.rename(
            columns={
                "Time": "DateTime",
                "Tag": "Animal",
                "Consumption": f"Consumption{DATA_SUFFIX}",
            },
            inplace=True,
        )

        df.drop(
            columns=[
                "DeviceId",
            ],
            inplace=True,
        )

        # Remove records without animal assignment
        df.dropna(subset=["Animal"], inplace=True)

        # Set columns order
        df = df[["DateTime", "Animal", f"Consumption{DATA_SUFFIX}"]]

        variables = {
            f"Consumption{DATA_SUFFIX}": Variable(
                f"Consumption{DATA_SUFFIX}",
                "g",
                "ConsumptionScale intake",
                "float64",
                Aggregation.SUM,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, variables
