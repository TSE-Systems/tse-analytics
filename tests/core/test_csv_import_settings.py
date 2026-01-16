"""
Unit tests for tse_analytics.core.csv_import_settings module.
"""

import pytest

from tse_analytics.core.csv_import_settings import CsvImportSettings


class TestCsvImportSettings:
    """Tests for CsvImportSettings class."""

    def test_initialization(self):
        """Test that CsvImportSettings can be initialized with parameters."""
        settings = CsvImportSettings(
            delimiter=",",
            decimal_separator=".",
            day_first=True,
            use_datetime_format=False,
            datetime_format="%Y-%m-%d %H:%M:%S",
        )

        assert settings.delimiter == ","
        assert settings.decimal_separator == "."
        assert settings.day_first is True
        assert settings.use_datetime_format is False
        assert settings.datetime_format == "%Y-%m-%d %H:%M:%S"

    def test_delimiter_attribute(self):
        """Test that delimiter attribute is correctly set."""
        settings = CsvImportSettings(
            delimiter="\t",
            decimal_separator=",",
            day_first=False,
            use_datetime_format=True,
            datetime_format="%d/%m/%Y",
        )

        assert settings.delimiter == "\t"

    def test_decimal_separator_attribute(self):
        """Test that decimal_separator attribute is correctly set."""
        settings = CsvImportSettings(
            delimiter=";",
            decimal_separator=",",
            day_first=True,
            use_datetime_format=False,
            datetime_format="",
        )

        assert settings.decimal_separator == ","

    def test_day_first_attribute(self):
        """Test that day_first attribute is correctly set."""
        settings = CsvImportSettings(
            delimiter=",",
            decimal_separator=".",
            day_first=False,
            use_datetime_format=False,
            datetime_format="",
        )

        assert settings.day_first is False

    def test_use_datetime_format_attribute(self):
        """Test that use_datetime_format attribute is correctly set."""
        settings = CsvImportSettings(
            delimiter=",",
            decimal_separator=".",
            day_first=True,
            use_datetime_format=True,
            datetime_format="%Y-%m-%d",
        )

        assert settings.use_datetime_format is True

    def test_datetime_format_attribute(self):
        """Test that datetime_format attribute is correctly set."""
        datetime_fmt = "%d.%m.%Y %H:%M:%S.%f"
        settings = CsvImportSettings(
            delimiter=";",
            decimal_separator=",",
            day_first=True,
            use_datetime_format=True,
            datetime_format=datetime_fmt,
        )

        assert settings.datetime_format == datetime_fmt

    def test_get_default_returns_settings(self):
        """Test that get_default returns a CsvImportSettings instance."""
        settings = CsvImportSettings.get_default()

        assert isinstance(settings, CsvImportSettings)

    def test_get_default_values(self):
        """Test that get_default returns correct default values."""
        settings = CsvImportSettings.get_default()

        assert settings.delimiter == ";"
        assert settings.decimal_separator == "."
        assert settings.day_first is True
        assert settings.use_datetime_format is False
        assert settings.datetime_format == "%Y-%m-%d %H:%M:%S.%f"

    def test_get_default_is_static_method(self):
        """Test that get_default can be called without instantiation."""
        # This should not raise an error
        settings = CsvImportSettings.get_default()
        assert settings is not None

    def test_multiple_instances_independent(self):
        """Test that multiple instances are independent."""
        settings1 = CsvImportSettings(
            delimiter=",",
            decimal_separator=".",
            day_first=True,
            use_datetime_format=False,
            datetime_format="%Y-%m-%d",
        )

        settings2 = CsvImportSettings(
            delimiter=";",
            decimal_separator=",",
            day_first=False,
            use_datetime_format=True,
            datetime_format="%d/%m/%Y",
        )

        assert settings1.delimiter != settings2.delimiter
        assert settings1.decimal_separator != settings2.decimal_separator
        assert settings1.day_first != settings2.day_first
        assert settings1.use_datetime_format != settings2.use_datetime_format
        assert settings1.datetime_format != settings2.datetime_format

    def test_custom_delimiter_values(self):
        """Test various delimiter values."""
        delimiters = [",", ";", "\t", "|", " "]
        for delim in delimiters:
            settings = CsvImportSettings(
                delimiter=delim,
                decimal_separator=".",
                day_first=True,
                use_datetime_format=False,
                datetime_format="",
            )
            assert settings.delimiter == delim

    def test_custom_decimal_separator_values(self):
        """Test various decimal separator values."""
        separators = [".", ","]
        for sep in separators:
            settings = CsvImportSettings(
                delimiter=";",
                decimal_separator=sep,
                day_first=True,
                use_datetime_format=False,
                datetime_format="",
            )
            assert settings.decimal_separator == sep

    def test_different_datetime_formats(self):
        """Test various datetime format strings."""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y-%m-%d %H:%M:%S.%f",
            "%d.%m.%Y",
        ]
        for fmt in formats:
            settings = CsvImportSettings(
                delimiter=",",
                decimal_separator=".",
                day_first=True,
                use_datetime_format=True,
                datetime_format=fmt,
            )
            assert settings.datetime_format == fmt
