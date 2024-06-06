class CsvImportSettings:
    def __init__(
        self,
        delimiter: str,
        decimal_separator: str,
        day_first: bool,
        use_datetime_format: bool,
        datetime_format: str,
    ):
        self.delimiter = delimiter
        self.decimal_separator = decimal_separator
        self.day_first = day_first
        self.use_datetime_format = use_datetime_format
        self.datetime_format = datetime_format

    @staticmethod
    def get_default():
        settings = CsvImportSettings(
            ";",
            ".",
            True,
            False,
            datetime_format="%Y-%m-%d %H:%M:%S.%f",
        )
        return settings
