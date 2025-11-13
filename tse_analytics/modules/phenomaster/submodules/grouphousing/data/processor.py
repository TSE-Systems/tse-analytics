from datetime import datetime

import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


def preprocess_trafficage_datatable(dataset: PhenoMasterDataset, df: pd.DataFrame) -> Datatable:
    df = df.copy()

    # Rename columns to be compatible with Datatable format
    df.rename(columns={"StartDateTime": "DateTime"}, inplace=True)
    df.drop(columns=["EndDateTime"], inplace=True)

    # Calculate time delta
    first_timestamp = df["DateTime"].min()
    if first_timestamp > dataset.experiment_started:
        first_timestamp = dataset.experiment_started
    df.insert(df.columns.get_loc("DateTime") + 1, "Timedelta", df["DateTime"] - first_timestamp)

    now = datetime.now()
    now_string = now.strftime("%Y-%m-%d %H:%M:%S")

    variables = {
        "Activity": Variable(
            "Activity",
            "[cnt]",
            "Activity index",
            "int64",
            Aggregation.MAX,
            False,
        ),
        "Distance": Variable(
            "Distance",
            "",
            "Relative distance",
            "float64",
            Aggregation.SUM,
            False,
        ),
    }

    datatable = Datatable(
        dataset,
        f"TraffiCage [{now_string}]",
        "TraffiCage data",
        variables,
        df,
        None,
    )

    return datatable
