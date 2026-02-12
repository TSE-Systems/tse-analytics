"""Tests for tse_analytics.core.data.shared module."""

import pandas as pd
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    AnimalDiet,
    Factor,
    FactorLevel,
    SplitMode,
    TimePhase,
    Variable,
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


class TestSplitMode:
    """Tests for SplitMode enum."""

    def test_values(self):
        assert SplitMode.ANIMAL == "Animal"
        assert SplitMode.FACTOR == "Factor"
        assert SplitMode.RUN == "Run"
        assert SplitMode.TOTAL == "Total"

    def test_is_str(self):
        assert isinstance(SplitMode.ANIMAL, str)


class TestAnimal:
    """Tests for Animal dataclass."""

    def test_creation(self):
        animal = Animal(enabled=True, id="A1", color="#FF0000", properties={"weight": 25.0})
        assert animal.id == "A1"
        assert animal.enabled is True
        assert animal.color == "#FF0000"
        assert animal.properties == {"weight": 25.0}

    def test_get_dict(self):
        animal = Animal(enabled=True, id="A1", color="#FF0000", properties={})
        d = animal.get_dict()
        assert "id" in d
        assert "enabled" in d
        assert "color" in d
        assert "properties" in d
        assert d["id"] == "A1"

    def test_get_dict_returns_all_fields(self):
        animal = Animal(enabled=False, id="B2", color="#00FF00", properties={"cage": 3})
        d = animal.get_dict()
        assert len(d) == 4


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
        factor = Factor(name="Diet", levels=levels)
        assert factor.name == "Diet"
        assert len(factor.levels) == 1

    def test_default_levels(self):
        factor = Factor(name="Empty")
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
        d = var.get_dict()
        assert "name" in d
        assert "unit" in d
        assert "aggregation" in d
        assert d["name"] == "Speed"


class TestTimePhase:
    """Tests for TimePhase dataclass."""

    def test_creation(self):
        phase = TimePhase(name="Light", start_timestamp=pd.Timedelta("7h"))
        assert phase.name == "Light"
        assert phase.start_timestamp == pd.Timedelta("7h")


class TestAnimalDiet:
    """Tests for AnimalDiet dataclass."""

    def test_creation(self):
        diet = AnimalDiet(name="Standard", caloric_value=3.5)
        assert diet.name == "Standard"
        assert diet.caloric_value == 3.5
