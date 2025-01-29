from dataclasses import dataclass


@dataclass
class TseImportSettings:
    import_calo_bin: bool
    import_drinkfeed_bin: bool
    import_actimot_raw: bool
