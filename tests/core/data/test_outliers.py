"""Tests for tse_analytics.core.data.outliers module."""

from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings


class TestOutliersMode:
    """Tests for OutliersMode enum."""

    def test_values(self):
        assert OutliersMode.OFF == "Outliers detection off"
        assert OutliersMode.HIGHLIGHT == "Highlight outliers"
        assert OutliersMode.REMOVE == "Remove outliers"

    def test_is_str(self):
        assert isinstance(OutliersMode.OFF, str)


class TestOutliersSettings:
    """Tests for OutliersSettings."""

    def test_stores_values(self):
        settings = OutliersSettings(OutliersMode.REMOVE, 1.5)
        assert settings.mode == OutliersMode.REMOVE
        assert settings.coefficient == 1.5

    def test_off_mode(self):
        settings = OutliersSettings(OutliersMode.OFF, 2.0)
        assert settings.mode == OutliersMode.OFF
        assert settings.coefficient == 2.0
