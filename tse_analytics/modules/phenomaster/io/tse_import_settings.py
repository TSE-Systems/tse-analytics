from dataclasses import dataclass


CHUNK_SIZE = 1000000

MAIN_TABLE = "main_table"
ACTIMOT_RAW_TABLE = "actimot_raw"
DRINKFEED_BIN_TABLE = "drinkfeed_bin"
CALO_BIN_TABLE = "calo_bin"
GROUP_HOUSING_TABLE = "group_housing"


@dataclass
class TseImportSettings:
    import_calo_bin: bool
    import_drinkfeed_bin: bool
    import_actimot_raw: bool
    import_grouphousing: bool
