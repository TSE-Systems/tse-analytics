from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.io import tse_import_settings


VARIABLES_TO_REMOVE = [
    "VO2(1)",
    "VO2(2)",
    "VCO2(1)",
    "VCO2(2)",
    "H(1)",
    "H(2)",
]


VARIABLES_TO_RENAME = {
    "H(3)": "EE",
    "VO2(3)": "VO2",
    "VCO2(3)": "VCO2",
}


def cleanup_variables(dataset: PhenoMasterDataset) -> None:
    for variable in VARIABLES_TO_REMOVE:
        dataset.metadata["tables"][tse_import_settings.MAIN_TABLE]["columns"].pop(variable, None)

    for old_name, new_name in VARIABLES_TO_RENAME.items():
        if old_name in dataset.metadata["tables"][tse_import_settings.MAIN_TABLE]["columns"]:
            dataset.metadata["tables"][tse_import_settings.MAIN_TABLE]["columns"][new_name] = dataset.metadata[
                "tables"
            ][tse_import_settings.MAIN_TABLE]["columns"].pop(old_name, None)
            dataset.metadata["tables"][tse_import_settings.MAIN_TABLE]["columns"][new_name]["id"] = new_name

    for table in dataset.datatables.values():
        table.delete_variables(VARIABLES_TO_REMOVE)
        table.rename_variables(VARIABLES_TO_RENAME)

    # Process calo_bin data
    if isinstance(dataset, PhenoMasterDataset):
        if hasattr(dataset, "calo_data") and dataset.calo_data is not None:
            for var_name in VARIABLES_TO_REMOVE:
                dataset.calo_data.variables.pop(var_name, None)

            for old_name, new_name in VARIABLES_TO_RENAME.items():
                if old_name in dataset.calo_data.variables:
                    dataset.calo_data.variables[new_name] = dataset.calo_data.variables.pop(old_name, None)
                    dataset.calo_data.variables[new_name].name = new_name

            dataset.calo_data.raw_df.drop(columns=VARIABLES_TO_REMOVE, inplace=True, errors="ignore")
            dataset.calo_data.raw_df.rename(columns=VARIABLES_TO_RENAME, inplace=True, errors="ignore")
