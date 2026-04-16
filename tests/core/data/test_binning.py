"""Tests for tse_analytics.core.data.binning module."""

from datetime import time, timedelta

from tse_analytics.core.data.binning import (
    BinningMode,
    BinningSettings,
    TimeCyclesBinningSettings,
    TimeIntervalsBinningSettings,
    TimePhase,
    TimePhasesBinningSettings,
)


class TestBinningMode:
    """Tests for BinningMode enum."""

    def test_values(self):
        assert BinningMode.INTERVALS == "Time Intervals"
        assert BinningMode.CYCLES == "Light/Dark Cycles"
        assert BinningMode.PHASES == "Time Phases"


class TestBinningSettings:
    """Tests for BinningSettings default values."""

    def test_defaults(self):
        settings = BinningSettings()
        assert isinstance(settings.time_cycles_settings, TimeCyclesBinningSettings)
        assert isinstance(settings.time_phases_settings, TimePhasesBinningSettings)

    def test_default_cycle_settings(self):
        settings = BinningSettings()
        assert settings.time_cycles_settings.light_cycle_start == time(7, 0)
        assert settings.time_cycles_settings.dark_cycle_start == time(19, 0)

    def test_default_phases_settings(self):
        settings = BinningSettings()
        assert settings.time_phases_settings.time_phases == []


class TestTimeIntervalsBinningSettings:
    """Tests for TimeIntervalsBinningSettings."""

    def test_stores_values(self):
        settings = TimeIntervalsBinningSettings("minute", 30)
        assert settings.unit == "minute"
        assert settings.delta == 30


class TestTimeCyclesBinningSettings:
    """Tests for TimeCyclesBinningSettings."""

    def test_stores_values(self):
        settings = TimeCyclesBinningSettings(time(6, 0), time(18, 0))
        assert settings.light_cycle_start == time(6, 0)
        assert settings.dark_cycle_start == time(18, 0)


class TestTimePhasesBinningSettings:
    """Tests for TimePhasesBinningSettings."""

    def test_stores_phases(self):
        phases = [
            TimePhase(name="Phase1", start_timestamp=timedelta(0)),
            TimePhase(name="Phase2", start_timestamp=timedelta(hours=12)),
        ]
        settings = TimePhasesBinningSettings(phases)
        assert len(settings.time_phases) == 2
        assert settings.time_phases[0].name == "Phase1"

    def test_empty_phases(self):
        settings = TimePhasesBinningSettings([])
        assert settings.time_phases == []
