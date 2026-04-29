"""Tests for tse_analytics.core.data.shared module."""

from dataclasses import asdict
from datetime import time, timedelta

import pytest
from pydantic import TypeAdapter, ValidationError
from tse_analytics.core.data.binning import TimePhase
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    AnimalDiet,
    ByAnimalConfig,
    ByAnimalPropertyConfig,
    ByColumnConfig,
    ByElapsedTimeConfig,
    ByTimeOfDayConfig,
    Factor,
    FactorLevel,
    FactorRole,
    FactorSource,
    Variable,
)
from tse_analytics.core.data.shared import (
    TimePhase as SharedTimePhase,
)


class TestAggregation:
    """Tests for Aggregation enum."""

    def test_values(self):
        assert Aggregation.MEAN == "mean"
        assert Aggregation.MEDIAN == "median"
        assert Aggregation.SUM == "sum"
        assert Aggregation.MIN == "min"
        assert Aggregation.MAX == "max"

    def test_membership(self):
        assert "mean" in Aggregation.__members__.values()
        assert "invalid" not in Aggregation.__members__.values()

    def test_is_str(self):
        assert isinstance(Aggregation.MEAN, str)


class TestAnimal:
    """Tests for Animal dataclass."""

    def test_creation(self):
        animal = Animal(id="A1", color="#FF0000", properties={"weight": 25.0})
        assert animal.id == "A1"
        assert animal.color == "#FF0000"
        assert animal.properties == {"weight": 25.0}

    def test_get_dict(self):
        animal = Animal(id="A1", color="#FF0000", properties={})
        d = asdict(animal)
        assert "id" in d
        assert "color" in d
        assert "properties" in d
        assert d["id"] == "A1"

    def test_get_dict_returns_all_fields(self):
        animal = Animal(id="B2", color="#00FF00", properties={"cage": 3})
        d = asdict(animal)
        assert len(d) == 3


class TestFactorLevel:
    """Tests for FactorLevel dataclass."""

    def test_creation(self):
        level = FactorLevel(name="Control", color="#FF0000", animal_ids=["A1", "A2"])
        assert level.name == "Control"
        assert level.animal_ids == ["A1", "A2"]

    def test_default_animal_ids(self):
        level = FactorLevel(name="Empty", color="#000000")
        assert level.animal_ids == []


class TestFactor:
    """Tests for Factor dataclass."""

    def test_creation(self):
        levels = [FactorLevel(name="L1", color="#FF0000")]
        factor = Factor(name="Diet", config=ByAnimalConfig(), role=FactorRole.BETWEEN_SUBJECT, levels=levels)
        assert factor.name == "Diet"
        assert len(factor.levels) == 1

    def test_default_levels(self):
        factor = Factor(name="Empty", config=ByAnimalConfig(), role=FactorRole.BETWEEN_SUBJECT)
        assert factor.levels == []


class TestVariable:
    """Tests for Variable dataclass."""

    def test_creation(self):
        var = Variable(
            name="Weight",
            unit="g",
            description="Body weight",
            type="float",
            aggregation=Aggregation.MEAN,
            remove_outliers=True,
        )
        assert var.name == "Weight"
        assert var.unit == "g"
        assert var.aggregation == Aggregation.MEAN
        assert var.remove_outliers is True

    def test_get_dict(self):
        var = Variable(
            name="Speed",
            unit="m/s",
            description="Speed",
            type="float",
            aggregation=Aggregation.SUM,
            remove_outliers=False,
        )
        d = asdict(var)
        assert "name" in d
        assert "unit" in d
        assert "aggregation" in d
        assert d["name"] == "Speed"


class TestTimePhase:
    """Tests for TimePhase dataclass."""

    def test_creation(self):
        phase = TimePhase(name="Light", start_timestamp=timedelta(hours=7))
        assert phase.name == "Light"
        assert phase.start_timestamp == timedelta(hours=7)


class TestAnimalDiet:
    """Tests for AnimalDiet dataclass."""

    def test_creation(self):
        diet = AnimalDiet(name="Standard", caloric_value=3.5)
        assert diet.name == "Standard"
        assert diet.caloric_value == 3.5


class TestFactorRoleDefaults:
    """Validates that ``role`` is auto-defaulted from ``config`` when not given."""

    def test_by_animal_defaults_to_between_subject(self):
        factor = Factor(name="Diet", config=ByAnimalConfig(), role=FactorRole.BETWEEN_SUBJECT)
        assert factor.role == FactorRole.BETWEEN_SUBJECT

    def test_by_animal_property_defaults_to_between_subject(self):
        factor = Factor(
            name="Genotype", config=ByAnimalPropertyConfig(property_key="Genotype"), role=FactorRole.BETWEEN_SUBJECT
        )
        assert factor.role == FactorRole.BETWEEN_SUBJECT

    def test_by_time_of_day_defaults_to_within_subject(self):
        factor = Factor(
            name="LC",
            config=ByTimeOfDayConfig(
                light_cycle_start=time(7, 0),
                dark_cycle_start=time(19, 0),
            ),
            role=FactorRole.WITHIN_SUBJECT,
        )
        assert factor.role == FactorRole.WITHIN_SUBJECT

    def test_by_elapsed_time_defaults_to_within_subject(self):
        factor = Factor(
            name="Phases",
            config=ByElapsedTimeConfig(
                phases=[SharedTimePhase(name="P", start_timestamp=timedelta(0))],
            ),
            role=FactorRole.WITHIN_SUBJECT,
        )
        assert factor.role == FactorRole.WITHIN_SUBJECT


class TestFactorRoleSourceValidation:
    """Incompatible ``role`` / ``config.source`` combinations must be rejected."""

    def test_by_column_accepts_either_role(self):
        between = Factor(
            name="ColB",
            role=FactorRole.BETWEEN_SUBJECT,
            config=ByColumnConfig(column="Cohort"),
        )
        within = Factor(
            name="ColW",
            role=FactorRole.WITHIN_SUBJECT,
            config=ByColumnConfig(column="Trial"),
        )
        assert between.role == FactorRole.BETWEEN_SUBJECT
        assert within.role == FactorRole.WITHIN_SUBJECT


class TestFactorSerializationRoundTrip:
    """Round-trips ``Factor`` through pydantic's TypeAdapter to confirm storage compatibility."""

    def _round_trip(self, factor: Factor) -> Factor:
        adapter = TypeAdapter(Factor)
        return adapter.validate_python(adapter.dump_python(factor))

    def test_by_time_of_day_round_trips(self):
        factor = Factor(
            name="LightCycle",
            config=ByTimeOfDayConfig(
                light_cycle_start=time(7, 0),
                dark_cycle_start=time(19, 0),
            ),
            role=FactorRole.WITHIN_SUBJECT,
        )
        result = self._round_trip(factor)
        assert isinstance(result.config, ByTimeOfDayConfig)
        assert result.role == FactorRole.WITHIN_SUBJECT
        assert result.config.light_cycle_start == time(7, 0)

    def test_discriminated_config_serializes_with_source_key(self):
        factor = Factor(
            name="Diet",
            config=ByAnimalPropertyConfig(property_key="Genotype"),
            role=FactorRole.BETWEEN_SUBJECT,
        )
        dumped = TypeAdapter(Factor).dump_python(factor)
        assert dumped["config"]["source"] == FactorSource.BY_ANIMAL_PROPERTY
        assert dumped["config"]["property_key"] == "Genotype"

    def test_dict_of_factors_round_trips(self):
        """Mirrors the storage.py serialization shape."""
        factors = {
            "LightCycle": Factor(
                name="LightCycle",
                config=ByTimeOfDayConfig(
                    light_cycle_start=time(7, 0),
                    dark_cycle_start=time(19, 0),
                ),
                role=FactorRole.WITHIN_SUBJECT,
            ),
            "Treatment": Factor(
                name="Treatment",
                config=ByAnimalConfig(),
                role=FactorRole.BETWEEN_SUBJECT,
                levels=[FactorLevel(name="Control", color="#000000", animal_ids=["A1"])],
            ),
        }
        adapter = TypeAdapter(dict[str, Factor])
        result = adapter.validate_python(adapter.dump_python(factors))
        assert set(result) == {"LightCycle", "Treatment"}
        assert result["LightCycle"].role == FactorRole.WITHIN_SUBJECT
        assert result["Treatment"].role == FactorRole.BETWEEN_SUBJECT
