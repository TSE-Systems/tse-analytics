"""
Module for outlier detection and handling in data analysis.

This module provides classes for configuring outlier detection and handling,
including different modes (off, highlight, remove) and settings.
"""

from enum import StrEnum, unique

from pydantic.dataclasses import dataclass


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


@unique
class OutliersType(StrEnum):
    IQR = "Interquartile Range (IQR)"
    ZSCORE = "Z-Score"
    THRESHOLDS = "Thresholds"


@dataclass
class OutliersSettings:
    """
    Settings for outlier detection and handling.

    This class holds the configuration for outlier detection, including the mode
    and coefficient for determining what constitutes an outlier.
    """

    mode: OutliersMode = OutliersMode.OFF
    type: OutliersType = OutliersType.IQR
    iqr_multiplier: float = 1.5
    min_threshold_enabled: bool = False
    min_threshold: float = 0.0
    max_threshold_enabled: bool = False
    max_threshold: float = 0.0
