"""Tests for tse_analytics.toolbox.data_plot.processor module."""

from datetime import time

import pandas as pd
import pytest
from tse_analytics.core.data.shared import ByTimeOfDayConfig
from tse_analytics.toolbox.data_plot.processor import compute_dark_band_spans

# Standard cycle: light 06:00–18:00, dark 18:00–06:00
STANDARD = ByTimeOfDayConfig(light_cycle_start=time(6, 0), dark_cycle_start=time(18, 0))
# Reversed cycle (dark by day): dark 07:00–19:00, light 19:00–07:00
REVERSED = ByTimeOfDayConfig(light_cycle_start=time(19, 0), dark_cycle_start=time(7, 0))


class TestComputeDarkBandSpans:
    """Tests for the dark-cycle shading span computation."""

    @pytest.mark.parametrize(
        ("config", "started", "max_hours", "expected"),
        [
            # Morning start, during the light phase: leading (stepped-back) band is skipped.
            (STANDARD, "2024-01-01 06:00:00", 24.0, [(12.0, 24.0)]),
            # Evening start, already inside the dark phase: leading partial dark band shaded from 0.
            (STANDARD, "2024-01-01 22:00:00", 24.0, [(0.0, 8.0), (20.0, 24.0)]),
            # Noon start.
            (STANDARD, "2024-01-01 12:00:00", 24.0, [(6.0, 18.0)]),
            # Reversed (dark-by-day) cycle, starting inside the dark phase.
            (REVERSED, "2024-01-01 08:00:00", 24.0, [(0.0, 11.0), (23.0, 24.0)]),
            # Range spanning multiple days repeats the bands every 24 h.
            (STANDARD, "2024-01-01 06:00:00", 48.0, [(12.0, 24.0), (36.0, 48.0)]),
        ],
    )
    def test_spans(self, config, started, max_hours, expected):
        spans = compute_dark_band_spans(config, pd.Timestamp(started), max_hours)
        assert spans == expected

    def test_degenerate_cycle_returns_empty(self):
        """A zero-length dark cycle produces no bands instead of a wrong full-day shade."""
        config = ByTimeOfDayConfig(light_cycle_start=time(6, 0), dark_cycle_start=time(6, 0))
        assert compute_dark_band_spans(config, pd.Timestamp("2024-01-01 06:00:00"), 24.0) == []
