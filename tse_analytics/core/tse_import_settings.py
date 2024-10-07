from dataclasses import dataclass


@dataclass
class TseImportSettings:
    import_calo: bool
    import_meal: bool
    import_actimot: bool
