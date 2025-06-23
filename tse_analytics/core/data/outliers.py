"""
Module for outlier detection and handling in data analysis.

This module provides classes for configuring outlier detection and handling,
including different modes (off, highlight, remove) and settings.
"""

from enum import StrEnum, unique


@unique
class OutliersMode(StrEnum):
    """
    Enumeration of available outlier detection modes.

    Attributes
    ----------
    OFF : str
        Outlier detection is turned off.
    HIGHLIGHT : str
        Outliers are highlighted but not removed.
    REMOVE : str
        Outliers are removed from the data.
    """

    OFF = "Outliers detection off"
    HIGHLIGHT = "Highlight outliers"
    REMOVE = "Remove outliers"


class OutliersSettings:
    """
    Settings for outlier detection and handling.

    This class holds the configuration for outlier detection, including the mode
    and coefficient for determining what constitutes an outlier.
    """

    def __init__(self, mode: OutliersMode, coefficient: float):
        """
        Initialize outlier detection settings.

        Parameters
        ----------
        mode : OutliersMode
            The mode for handling outliers (OFF, HIGHLIGHT, or REMOVE).
        coefficient : float
            The coefficient used to determine outliers (typically used with IQR method).
        """
        self.mode = mode
        self.coefficient = coefficient
