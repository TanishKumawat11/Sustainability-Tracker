"""
Unit tests for tracker/models.py

Tests:
- Activity calculates impact correctly for each category
- Activity auto-assigns the correct unit per category
- Activity.to_dict() / from_dict() round-trip serialisation
- SustainabilityGoal validates the target on construction
"""

import datetime
import pytest

from tracker.models import Activity, SustainabilityGoal
from tracker.factors import EnvironmentalFactors
from tracker.exceptions import InvalidGoalError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_activity(category: str, amount: float) -> Activity:
    """Create a simple Activity for the given category and amount."""
    return Activity(
        category=category,
        amount=amount,
        description="test",
        date=datetime.date.today(),
    )


# ---------------------------------------------------------------------------
# Activity — impact calculation
# ---------------------------------------------------------------------------

class TestActivityImpact:
    def test_transportation_impact(self):
        activity = make_activity("Transportation", 100.0)
        expected = round(100.0 * EnvironmentalFactors.IMPACT_FACTORS["Transportation"], 4)
        assert activity.impact == expected

    def test_energy_impact(self):
        activity = make_activity("Energy", 50.0)
        expected = round(50.0 * EnvironmentalFactors.IMPACT_FACTORS["Energy"], 4)
        assert activity.impact == expected

    def test_water_impact_passthrough(self):
        activity = make_activity("Water", 200.0)
        assert activity.impact == 200.0  # factor is 1.0

    def test_waste_impact_passthrough(self):
        activity = make_activity("Waste", 15.0)
        assert activity.impact == 15.0  # factor is 1.0

    def test_impact_is_rounded_to_4dp(self):
        # 1 km * 0.21 = 0.21 exactly — test a value that exercises rounding
        activity = make_activity("Transportation", 3.0)
        assert activity.impact == round(3.0 * 0.21, 4)


# ---------------------------------------------------------------------------
# Activity — unit auto-assignment
# ---------------------------------------------------------------------------

class TestActivityUnit:
    def test_transportation_unit(self):
        assert make_activity("Transportation", 1.0).unit == "km"

    def test_energy_unit(self):
        assert make_activity("Energy", 1.0).unit == "kWh"

    def test_water_unit(self):
        assert make_activity("Water", 1.0).unit == "litres"

    def test_waste_unit(self):
        assert make_activity("Waste", 1.0).unit == "kg"


# ---------------------------------------------------------------------------
# Activity — serialisation round-trip
# ---------------------------------------------------------------------------

class TestActivitySerialisation:
    def test_to_dict_keys(self):
        a = make_activity("Energy", 10.0)
        d = a.to_dict()
        assert set(d.keys()) == {"id", "category", "amount", "unit", "description", "date", "impact"}

    def test_to_dict_date_is_string(self):
        a = make_activity("Transportation", 5.0)
        d = a.to_dict()
        assert isinstance(d["date"], str)

    def test_round_trip(self):
        original = Activity(
            category="Waste",
            amount=7.5,
            description="Weekly recycling",
            date=datetime.date(2025, 6, 15),
        )
        restored = Activity.from_dict(original.to_dict())

        assert restored.id == original.id
        assert restored.category == original.category
        assert restored.amount == original.amount
        assert restored.unit == original.unit
        assert restored.description == original.description
        assert restored.date == original.date
        assert restored.impact == original.impact

    def test_from_dict_missing_description_defaults_empty(self):
        a = make_activity("Water", 100.0)
        d = a.to_dict()
        del d["description"]
        restored = Activity.from_dict(d)
        assert restored.description == ""


# ---------------------------------------------------------------------------
# SustainabilityGoal
# ---------------------------------------------------------------------------

class TestSustainabilityGoal:
    def test_valid_goal(self):
        goal = SustainabilityGoal(100.0)
        assert goal.monthly_target_kg_co2 == 100.0

    def test_zero_target_raises(self):
        with pytest.raises(InvalidGoalError):
            SustainabilityGoal(0.0)

    def test_negative_target_raises(self):
        with pytest.raises(InvalidGoalError):
            SustainabilityGoal(-50.0)
