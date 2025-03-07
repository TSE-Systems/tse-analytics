import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-CS"


class ConsumptionScaleData:
    def __init__(
        self,
        im_dataset,
        name: str,
        consumption_df: pd.DataFrame,
        model_df: pd.DataFrame,
    ):
        self.im_dataset = im_dataset
        self.name = name
        self.device_ids: list[str] = im_dataset.devices["ConsumptionScale"]

        self.consumption_df = consumption_df
        self.model_df = model_df

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.consumption_df.copy()

        # Convert cumulative values to differential ones
        preprocessed_device_df = []
        device_ids = df["DeviceId"].unique().tolist()
        for i, device_id in enumerate(device_ids):
            device_data = df[df["DeviceId"] == device_id]
            device_data["Consumption"] = device_data["Consumption"].diff().fillna(df["Consumption"]).round(5)
            preprocessed_device_df.append(device_data)
        df = pd.concat(preprocessed_device_df, ignore_index=True, sort=False)

        tag_to_animal_map = {}
        for animal in self.im_dataset.animals.values():
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
