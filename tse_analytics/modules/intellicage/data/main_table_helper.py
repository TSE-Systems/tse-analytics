import pandas as pd

from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset


def preprocess_main_table(dataset: IntelliCageDataset, sampling_interval: pd.Timedelta) -> IntelliCageDataset:
    df = dataset.intellicage_data.visits_df.copy()

    variables = dataset.intellicage_data.visits_variables
    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    # Add Run column
    df.insert(loc=4, column="Run", value=1)

    # Rename Cage column to Box
    df.rename(
        columns={
            "Cage": "Box",
        },
        inplace=True,
    )

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
        "PlaceError": "int",
    })

    df.sort_values(by=["DateTime", "Animal"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    dataset.original_df = df
    dataset.active_df = dataset.original_df.copy()
    dataset.sampling_interval = sampling_interval

    dataset.variables = variables

    # Remove absent animals
    animal_ids = df["Animal"].unique().tolist()
    animals = {}
    for animal in dataset.animals.values():
        if animal.id in animal_ids:
            animals[animal.id] = animal
    dataset.animals = animals

    return dataset
