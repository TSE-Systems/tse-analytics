"""
Color management module for TSE Analytics.

This module provides functions for managing colors in the application, including
getting color tuples and hex values, and creating dictionaries mapping animals
and factor levels to colors.
"""

import seaborn as sns
from matplotlib.colors import rgb2hex

from tse_analytics.core.data.shared import Animal, Factor

colormap_name = "tab20"
cmap = sns.color_palette(colormap_name, as_cmap=True)
# cmap = distinctipy.get_colormap(distinctipy.get_colors(32, pastel_factor=0.8))


def get_color_tuple(index: int) -> tuple[float, float, float, float]:
    """
    Get a color tuple from the color map based on the index.

    If the index exceeds the number of colors in the color map,
    it wraps around to reuse colors.

    Args:
        index: The index of the color in the color map.

    Returns:
        A tuple of four float values representing RGBA color.
    """
    if index > cmap.N:
        index = index - (cmap.N * (index // cmap.N))
    return cmap(index)


def get_color_hex(index: int) -> str:
    """
    Get a color in hexadecimal format from the color map based on the index.

    Args:
        index: The index of the color in the color map.

    Returns:
        A string representing the color in hexadecimal format.
    """
    return rgb2hex(get_color_tuple(index))


def get_factor_level_color_hex(index: int) -> str:
    palette = sns.color_palette("deep")
    n_colors = len(palette)
    if index >= n_colors:
        index = index - (n_colors * (index // n_colors))
    color_tuple = palette[index]
    return rgb2hex(color_tuple)


def get_animal_to_color_dict(animals: dict[str, Animal]) -> dict[str, str]:
    """
    Create a dictionary mapping animal IDs to their colors.

    Args:
        animals: A dictionary mapping animal IDs to Animal objects.

    Returns:
        A dictionary mapping animal IDs to color strings.
    """
    result = {}
    for animal in animals.values():
        result[animal.id] = animal.color
    return result


def get_level_to_color_dict(factor: Factor) -> dict[str, str] | str:
    """
    Map factor level names to colors.

    Returns a single hex color when the factor has no pre-computed levels
    (e.g. ``BY_TIME_INTERVAL`` factors, where bin counts can be too large to
    enumerate usefully). seaborn and plotnine palettes accept a single color
    string and apply it to every group.

    Args:
        factor: A Factor object containing levels.

    Returns:
        A dict mapping level names to colors when levels are populated, or a
        single hex color string otherwise.
    """
    if not factor.levels:
        return get_factor_level_color_hex(0)
    return {level.name: level.color for level in factor.levels}


def get_run_to_color_dict(number_of_runs: int) -> dict[int, str]:
    result = {}
    for run in range(number_of_runs):
        result[run + 1] = get_factor_level_color_hex(run)
    return result
