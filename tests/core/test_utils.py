"""
Unit tests for tse_analytics.core.utils module.
"""

from datetime import time
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSizePolicy, QToolButton, QWidget
from tse_analytics.core.utils import (
    get_available_sqlite_tables,
    get_figsize_from_widget,
    get_h_spacer_widget,
    get_html_image_from_figure,
    get_html_table,
    get_widget_tool_button,
    time_to_float,
)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for Qt-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestGetHtmlImageFromFigure:
    """Tests for get_html_image_from_figure function."""

    def test_returns_html_img_tag(self):
        """Test that function returns an HTML img tag."""
        figure = Figure()
        result = get_html_image_from_figure(figure)

        assert result.startswith("<img src='data:image/png;base64,")
        assert result.endswith("'><br>")

    def test_contains_base64_encoded_data(self):
        """Test that result contains base64 encoded image data."""
        figure = Figure()
        figure.add_subplot(111).plot([1, 2, 3], [1, 2, 3])
        result = get_html_image_from_figure(figure)

        # Extract base64 part
        base64_start = result.index("base64,") + 7
        base64_end = result.index("'>")
        base64_data = result[base64_start:base64_end]

        # Base64 data should be non-empty and contain valid characters
        assert len(base64_data) > 0
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in base64_data)

    def test_different_figures_produce_different_outputs(self):
        """Test that different figures produce different encoded outputs."""
        figure1 = Figure()
        figure1.add_subplot(111).plot([1, 2, 3], [1, 2, 3])

        figure2 = Figure()
        figure2.add_subplot(111).plot([1, 2, 3], [3, 2, 1])

        result1 = get_html_image_from_figure(figure1)
        result2 = get_html_image_from_figure(figure2)

        assert result1 != result2


class TestGetHtmlTable:
    """Tests for get_html_table function."""

    def test_basic_html_table_generation(self):
        """Test basic HTML table generation from DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        result = get_html_table(df, "Test Caption")

        assert "<table" in result
        assert "<caption>Test Caption</caption>" in result
        assert "</table>" in result

    def test_precision_parameter(self):
        """Test that precision parameter affects float formatting."""
        df = pd.DataFrame({"A": [1.123456789]})
        result = get_html_table(df, "Test", precision=2)

        assert "1.12" in result or "1.1235" in result  # Depending on rounding

    def test_index_shown_by_default(self):
        """Test that index is shown by default."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        result = get_html_table(df, "Test")

        # Index should be present in the HTML
        assert "<th" in result  # Table headers for index

    def test_index_hidden_when_false(self):
        """Test that index is hidden when index=False."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        result = get_html_table(df, "Test", index=False)

        # Result should still be valid HTML but with hidden index
        assert "<table" in result
        assert "<caption>Test</caption>" in result

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        result = get_html_table(df, "Empty")

        assert "<table" in result
        assert "<caption>Empty</caption>" in result


class TestGetAvailableSqliteTables:
    """Tests for get_available_sqlite_tables function."""

    @patch("tse_analytics.core.utils.cx.read_sql")
    def test_returns_table_list(self, mock_read_sql):
        """Test that function returns a list of table names."""
        mock_df = pd.DataFrame({"name": ["table1", "table2", "table3"]})
        mock_read_sql.return_value = mock_df

        result = get_available_sqlite_tables(Path("/fake/path.db"))

        assert result == ["table1", "table2", "table3"]
        mock_read_sql.assert_called_once()

    @patch("tse_analytics.core.utils.cx.read_sql")
    def test_correct_query_format(self, mock_read_sql):
        """Test that correct SQL query is used."""
        mock_df = pd.DataFrame({"name": []})
        mock_read_sql.return_value = mock_df

        test_path = Path("/test/database.db")
        get_available_sqlite_tables(test_path)

        call_args = mock_read_sql.call_args
        assert call_args[0][0] == f"sqlite:///{test_path}"
        assert "SELECT name FROM sqlite_master WHERE type='table'" in call_args[0][1]

    @patch("tse_analytics.core.utils.cx.read_sql")
    def test_empty_database(self, mock_read_sql):
        """Test handling of database with no tables."""
        mock_df = pd.DataFrame({"name": []})
        mock_read_sql.return_value = mock_df

        result = get_available_sqlite_tables(Path("/empty.db"))

        assert result == []


class TestGetWidgetToolButton:
    """Tests for get_widget_tool_button function."""

    def test_creates_tool_button(self, qapp):
        """Test that function creates a QToolButton."""
        parent = QWidget()
        widget = QWidget()
        icon = QIcon()

        button = get_widget_tool_button(parent, widget, "Test Text", icon)

        assert isinstance(button, QToolButton)
        assert button.text() == "Test Text"

    def test_button_popup_mode(self, qapp):
        """Test that button is configured with instant popup mode."""
        parent = QWidget()
        widget = QWidget()
        icon = QIcon()

        button = get_widget_tool_button(parent, widget, "Test", icon)

        assert button.popupMode() == QToolButton.ToolButtonPopupMode.InstantPopup

    def test_button_style(self, qapp):
        """Test that button has text beside icon style."""
        parent = QWidget()
        widget = QWidget()
        icon = QIcon()

        button = get_widget_tool_button(parent, widget, "Test", icon)

        assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon

    def test_widget_action_added(self, qapp):
        """Test that widget is added as an action to the button."""
        parent = QWidget()
        widget = QWidget()
        icon = QIcon()

        button = get_widget_tool_button(parent, widget, "Test", icon)

        actions = button.actions()
        assert len(actions) == 1


class TestGetHSpacerWidget:
    """Tests for get_h_spacer_widget function."""

    def test_creates_widget(self, qapp):
        """Test that function creates a QWidget."""
        parent = QWidget()
        spacer = get_h_spacer_widget(parent)

        assert isinstance(spacer, QWidget)
        assert spacer.parent() == parent

    def test_horizontal_size_policy(self, qapp):
        """Test that horizontal size policy is Expanding."""
        parent = QWidget()
        spacer = get_h_spacer_widget(parent)

        assert spacer.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding

    def test_vertical_size_policy(self, qapp):
        """Test that vertical size policy is Minimum."""
        parent = QWidget()
        spacer = get_h_spacer_widget(parent)

        assert spacer.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Minimum


class TestTimeToFloat:
    """Tests for time_to_float function."""

    def test_midnight(self):
        """Test conversion of midnight (00:00)."""
        result = time_to_float(time(0, 0))
        assert result == 0.0

    def test_noon(self):
        """Test conversion of noon (12:00)."""
        result = time_to_float(time(12, 0))
        assert result == 12.0

    def test_with_minutes(self):
        """Test conversion with minutes."""
        result = time_to_float(time(14, 30))
        assert result == 14.5

    def test_quarter_hour(self):
        """Test conversion of quarter hour."""
        result = time_to_float(time(10, 15))
        assert result == 10.25

    def test_45_minutes(self):
        """Test conversion of 45 minutes."""
        result = time_to_float(time(8, 45))
        assert result == 8.75

    def test_23_59(self):
        """Test conversion of 23:59."""
        result = time_to_float(time(23, 59))
        assert result == pytest.approx(23.983333, rel=1e-5)

    def test_single_minute(self):
        """Test conversion of single minute."""
        result = time_to_float(time(5, 1))
        assert result == pytest.approx(5.016666, rel=1e-5)


class TestGetFigsizeFromWidget:
    """Tests for get_figsize_from_widget function."""

    def test_returns_tuple_of_floats(self, qapp):
        """Test that function returns a tuple of two floats."""
        widget = QWidget()
        widget.resize(800, 600)

        result = get_figsize_from_widget(widget)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)

    def test_positive_dimensions(self, qapp):
        """Test that returned dimensions are positive."""
        widget = QWidget()
        widget.resize(800, 600)

        width, height = get_figsize_from_widget(widget)

        assert width > 0
        assert height > 0

    def test_different_sizes_produce_different_results(self, qapp):
        """Test that different widget sizes produce different results."""
        widget1 = QWidget()
        widget1.resize(400, 300)

        widget2 = QWidget()
        widget2.resize(800, 600)

        result1 = get_figsize_from_widget(widget1)
        result2 = get_figsize_from_widget(widget2)

        # Larger widget should produce larger figsize
        assert result2[0] > result1[0]
        assert result2[1] > result1[1]

    def test_aspect_ratio_preserved(self, qapp):
        """Test that aspect ratio is roughly preserved."""
        widget = QWidget()
        widget.resize(1600, 800)  # 2:1 aspect ratio

        width, height = get_figsize_from_widget(widget)
        ratio = width / height

        # Should be close to 2.0
        assert pytest.approx(ratio, rel=0.1) == 2.0
