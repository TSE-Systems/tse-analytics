from tse_analytics.core.data.dataset import Dataset
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


def cleanup_variables(dataset: Dataset) -> None:
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

    for extension_data in dataset.raw_datatables.values():
        for table in extension_data.values():
            table.delete_variables(VARIABLES_TO_REMOVE)
            table.rename_variables(VARIABLES_TO_RENAME)
