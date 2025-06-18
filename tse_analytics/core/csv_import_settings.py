"""
CSV import settings module for TSE Analytics.

This module provides a class for managing CSV import settings, including
delimiter, decimal separator, date format, and datetime format.
"""


class CsvImportSettings:
    """
    Class for managing CSV import settings.

    This class stores settings used for importing CSV files, including
    delimiter, decimal separator, date format, and datetime format.
    """

    def __init__(
        self,
        delimiter: str,
        decimal_separator: str,
        day_first: bool,
        use_datetime_format: bool,
        datetime_format: str,
    ):
        """
        Initialize CSV import settings.

        Args:
            delimiter: The character used to separate fields in the CSV file.
            decimal_separator: The character used as decimal separator in numeric values.
            day_first: Whether the day comes before month in date strings.
            use_datetime_format: Whether to use a specific datetime format for parsing.
            datetime_format: The format string for parsing datetime values.
        """
        self.delimiter = delimiter
        self.decimal_separator = decimal_separator
        self.day_first = day_first
        self.use_datetime_format = use_datetime_format
        self.datetime_format = datetime_format

    @staticmethod
    def get_default():
        """
        Get default CSV import settings.

        Returns:
            A CsvImportSettings object with default settings.
        """
        settings = CsvImportSettings(
            ";",
            ".",
            True,
            False,
            datetime_format="%Y-%m-%d %H:%M:%S.%f",
        )
        return settings
