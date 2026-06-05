"""
Unit tests for tse_analytics.core.color_manager module.
"""

import pytest
from matplotlib.colors import rgb2hex
from tse_analytics.core.color_manager import (
    cmap,
    get_color_hex,
    get_color_tuple,
    get_factor_level_color_hex,
    get_level_to_color_dict,
)
from tse_analytics.core.data.shared import ByAnimalConfig, Factor, FactorLevel, FactorRole


class TestGetColorTuple:
    """Tests for get_color_tuple function."""

    def test_returns_rgba_tuple(self):
        """Test that function returns a tuple with 4 values."""
        result = get_color_tuple(0)

        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_values_in_valid_range(self):
        """Test that RGBA values are in [0, 1] range."""
        result = get_color_tuple(5)

        for value in result:
            assert 0.0 <= value <= 1.0

    def test_different_indices_return_different_colors(self):
        """Test that different indices return different colors."""
        color1 = get_color_tuple(0)
        color2 = get_color_tuple(1)

        assert color1 != color2

    def test_wraps_around_when_exceeding_colormap_size(self):
        """Test that indices greater than colormap size wrap around."""
        # Get a color within range
        color_in_range = get_color_tuple(5)

        # Get the same color by wrapping around
        wrapped_index = 5 + cmap.N
        color_wrapped = get_color_tuple(wrapped_index)

        # They should be the same (or very close due to floating point)
        assert color_in_range == pytest.approx(color_wrapped)

    def test_index_zero(self):
        """Test that index 0 returns a valid color."""
        result = get_color_tuple(0)

        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_large_index_wrapping(self):
        """Test that very large indices wrap correctly."""
        # This should wrap multiple times
        result = get_color_tuple(100)

        assert isinstance(result, tuple)
        assert len(result) == 4
        for value in result:
            assert 0.0 <= value <= 1.0


class TestGetColorHex:
    """Tests for get_color_hex function."""

    def test_returns_hex_string(self):
        """Test that function returns a hex color string."""
        result = get_color_hex(0)

        assert isinstance(result, str)
        assert result.startswith("#")
        assert len(result) == 7  # #RRGGBB

    def test_hex_format_valid(self):
        """Test that returned hex string is valid."""
        result = get_color_hex(5)

        # Should be #RRGGBB format
        assert result[0] == "#"
        # All other characters should be valid hex digits
        assert all(c in "0123456789ABCDEFabcdef" for c in result[1:])

    def test_different_indices_return_different_hex(self):
        """Test that different indices return different hex colors."""
        hex1 = get_color_hex(0)
        hex2 = get_color_hex(1)

        assert hex1 != hex2

    def test_consistency_with_get_color_tuple(self):
        """Test that hex color matches the tuple color."""
        index = 3
        color_tuple = get_color_tuple(index)
        color_hex = get_color_hex(index)

        # Convert tuple to hex manually and compare
        expected_hex = rgb2hex(color_tuple)
        assert color_hex == expected_hex

    def test_wrapping_produces_same_hex(self):
        """Test that wrapped indices produce same hex colors."""
        hex1 = get_color_hex(2)
        hex2 = get_color_hex(2 + cmap.N)

        assert hex1 == hex2


class TestGetFactorLevelColorHex:
    """Tests for get_factor_level_color_hex function."""

    def test_returns_hex_string(self):
        """Test that function returns a hex color string."""
        result = get_factor_level_color_hex(0)

        assert isinstance(result, str)
        assert result.startswith("#")
        assert len(result) == 7

    def test_hex_format_valid(self):
        """Test that returned hex string is valid."""
        result = get_factor_level_color_hex(3)

        assert result[0] == "#"
        assert all(c in "0123456789ABCDEFabcdef" for c in result[1:])

    def test_different_indices_return_different_colors(self):
        """Test that different indices return different colors."""
        hex1 = get_factor_level_color_hex(0)
        hex2 = get_factor_level_color_hex(1)

        assert hex1 != hex2

    def test_wraps_around_when_exceeding_palette_size(self):
        """Test that indices wrap around for large values."""
        # Use deep palette which typically has 10 colors
        hex1 = get_factor_level_color_hex(2)
        hex2 = get_factor_level_color_hex(2 + 10)  # Wrapped index

        assert hex1 == hex2

    def test_index_zero(self):
        """Test that index 0 returns a valid color."""
        result = get_factor_level_color_hex(0)

        assert isinstance(result, str)
        assert result.startswith("#")


class TestGetLevelToColorDict:
    """Tests for get_level_to_color_dict function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        factor = Factor(
            name="Treatment",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Control": FactorLevel(name="Control", color="#FF0000", animal_ids=["a1"]),
                "Drug": FactorLevel(name="Drug", color="#00FF00", animal_ids=["a2"]),
            },
        )

        result = get_level_to_color_dict(factor)

        assert isinstance(result, dict)

    def test_maps_level_names_to_colors(self):
        """Test that level names are correctly mapped to their colors."""
        factor = Factor(
            name="Treatment",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Control": FactorLevel(name="Control", color="#FF0000", animal_ids=["a1"]),
                "Drug": FactorLevel(name="Drug", color="#00FF00", animal_ids=["a2"]),
            },
        )

        result = get_level_to_color_dict(factor)

        assert result["Control"] == "#FF0000"
        assert result["Drug"] == "#00FF00"

    def test_empty_factor_levels_returns_single_color(self):
        """Factors without populated levels (e.g. BY_TIME_INTERVAL) get a single hex color
        so seaborn/plotnine can still build a valid palette."""
        factor = Factor(name="Empty", config=ByAnimalConfig(), role=FactorRole.BETWEEN_SUBJECT, levels={})

        result = get_level_to_color_dict(factor)

        assert isinstance(result, str)
        assert result.startswith("#")

    def test_single_level(self):
        """Test with a factor having a single level."""
        factor = Factor(
            name="Simple",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={"Only": FactorLevel(name="Only", color="#0000FF", animal_ids=[])},
        )

        result = get_level_to_color_dict(factor)

        assert len(result) == 1
        assert result["Only"] == "#0000FF"

    def test_multiple_levels(self):
        """Test with multiple levels."""
        factor = Factor(
            name="MultiLevel",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Low": FactorLevel(name="Low", color="#111111", animal_ids=["a1"]),
                "Medium": FactorLevel(name="Medium", color="#222222", animal_ids=["a2"]),
                "High": FactorLevel(name="High", color="#333333", animal_ids=["a3"]),
            },
        )

        result = get_level_to_color_dict(factor)

        assert len(result) == 3
        assert result["Low"] == "#111111"
        assert result["Medium"] == "#222222"
        assert result["High"] == "#333333"

    def test_preserves_all_colors(self):
        """Test that all color values are preserved correctly."""
        factor = Factor(
            name="Test",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={
                "Alpha": FactorLevel(name="Alpha", color="#ABCDEF", animal_ids=["x"]),
                "Beta": FactorLevel(name="Beta", color="#FEDCBA", animal_ids=["y"]),
            },
        )

        result = get_level_to_color_dict(factor)

        assert result["Alpha"] == "#ABCDEF"
        assert result["Beta"] == "#FEDCBA"

    def test_different_factor_names_dont_affect_result(self):
        """Test that factor name doesn't affect the level-to-color mapping."""
        factor1 = Factor(
            name="FactorA",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={"Level1": FactorLevel(name="Level1", color="#111111", animal_ids=[])},
        )
        factor2 = Factor(
            name="FactorB",
            config=ByAnimalConfig(),
            role=FactorRole.BETWEEN_SUBJECT,
            levels={"Level1": FactorLevel(name="Level1", color="#111111", animal_ids=[])},
        )

        result1 = get_level_to_color_dict(factor1)
        result2 = get_level_to_color_dict(factor2)

        assert result1 == result2
