"""
Unit tests for tracker/services.py

Tests:
- add_activity() raises correct exceptions for invalid inputs
- total_carbon_emissions() sums Transportation + Energy only
- total_water_usage() sums Water only
- total_waste_generated() sums Waste only
- category_summary() returns all four categories
- get_progress() returns correct percentage
- get_recommendations() returns expected tips
"""

import datetime
import tempfile
from pathlib import Path

import pytest

from tracker.services import ActivityService
from tracker.models import SustainabilityGoal
from tracker.storage import StorageManager
from tracker.exceptions import (
    InvalidAmountError,
    InvalidCategoryError,
    InvalidDateError,
)


# ---------------------------------------------------------------------------
# Fixture: isolated service backed by a temporary JSON file
# ---------------------------------------------------------------------------

@pytest.fixture
def service(tmp_path: Path) -> ActivityService:
    """Return an ActivityService that writes to a temporary directory."""
    json_file = tmp_path / "activities.json"
    json_file.write_text("[]", encoding="utf-8")
    storage = StorageManager(file_path=json_file)
    return ActivityService(storage=storage)


@pytest.fixture
def today() -> datetime.date:
    return datetime.date.today()


@pytest.fixture
def yesterday() -> datetime.date:
    return datetime.date.today() - datetime.timedelta(days=1)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestAddActivityValidation:
    def test_zero_amount_raises(self, service, today):
        with pytest.raises(InvalidAmountError):
            service.add_activity("Transportation", 0.0, "test", today)

    def test_negative_amount_raises(self, service, today):
        with pytest.raises(InvalidAmountError):
            service.add_activity("Energy", -5.0, "test", today)

    def test_invalid_category_raises(self, service, today):
        with pytest.raises(InvalidCategoryError):
            service.add_activity("Cycling", 10.0, "test", today)

    def test_future_date_raises(self, service):
        future = datetime.date.today() + datetime.timedelta(days=1)
        with pytest.raises(InvalidDateError):
            service.add_activity("Water", 10.0, "test", future)

    def test_valid_activity_is_added(self, service, today):
        service.add_activity("Transportation", 10.0, "commute", today)
        assert len(service.get_all_activities()) == 1

    def test_today_date_is_valid(self, service, today):
        """The boundary: today should be accepted."""
        service.add_activity("Waste", 5.0, "recycling", today)
        assert len(service.get_all_activities()) == 1


# ---------------------------------------------------------------------------
# Aggregate totals
# ---------------------------------------------------------------------------

class TestAggregates:
    def _seed(self, service, today):
        """Add one activity of each category."""
        service.add_activity("Transportation", 100.0, "", today)   # 100 * 0.21 = 21.0 CO2
        service.add_activity("Energy", 50.0, "", today)             # 50 * 0.233 = 11.65 CO2
        service.add_activity("Water", 300.0, "", today)             # 300.0 litres
        service.add_activity("Waste", 10.0, "", today)              # 10.0 kg

    def test_total_carbon_includes_only_transport_and_energy(self, service, today):
        self._seed(service, today)
        expected = round(100.0 * 0.21 + 50.0 * 0.233, 2)
        assert service.total_carbon_emissions() == expected

    def test_total_water_includes_only_water(self, service, today):
        self._seed(service, today)
        assert service.total_water_usage() == 300.0

    def test_total_waste_includes_only_waste(self, service, today):
        self._seed(service, today)
        assert service.total_waste_generated() == 10.0

    def test_empty_totals_return_zero(self, service):
        assert service.total_carbon_emissions() == 0.0
        assert service.total_water_usage() == 0.0
        assert service.total_waste_generated() == 0.0

    def test_category_summary_has_all_categories(self, service, today):
        self._seed(service, today)
        summary = service.category_summary()
        assert set(summary.keys()) == {"Transportation", "Energy", "Water", "Waste"}

    def test_category_summary_values(self, service, today):
        self._seed(service, today)
        summary = service.category_summary()
        assert summary["Water"] == 300.0
        assert summary["Waste"] == 10.0
        assert summary["Transportation"] == round(100.0 * 0.21, 4)
        assert summary["Energy"] == round(50.0 * 0.233, 4)

    def test_category_summary_empty_categories_are_zero(self, service, today):
        service.add_activity("Water", 100.0, "", today)
        summary = service.category_summary()
        assert summary["Transportation"] == 0.0
        assert summary["Energy"] == 0.0
        assert summary["Waste"] == 0.0


# ---------------------------------------------------------------------------
# Progress toward goal
# ---------------------------------------------------------------------------

class TestGetProgress:
    def test_progress_within_goal(self, service, today):
        service.add_activity("Transportation", 100.0, "", today)  # 21.0 kg CO2
        goal = SustainabilityGoal(100.0)
        used, target, percent = service.get_progress(goal)
        assert used == 21.0
        assert target == 100.0
        assert percent == 21.0

    def test_progress_exceeds_goal_capped_at_100(self, service, today):
        service.add_activity("Transportation", 1000.0, "", today)  # 210.0 kg CO2
        goal = SustainabilityGoal(100.0)
        used, target, percent = service.get_progress(goal)
        assert used == 210.0
        assert percent == 100.0  # capped

    def test_progress_no_activities(self, service):
        goal = SustainabilityGoal(50.0)
        used, target, percent = service.get_progress(goal)
        assert used == 0.0
        assert percent == 0.0


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

class TestGetRecommendations:
    def test_no_activities_returns_start_prompt(self, service):
        tips = service.get_recommendations()
        assert len(tips) == 1
        assert "No activities recorded yet" in tips[0]

    def test_all_within_thresholds_returns_positive_tip(self, service, today):
        service.add_activity("Transportation", 10.0, "", today)  # 2.1 kg CO2 (under 50)
        tips = service.get_recommendations()
        assert any("Great work" in t for t in tips)

    def test_high_transport_triggers_tip(self, service, today):
        # Need > 50 kg CO2 from transportation: 50/0.21 ≈ 238.1 km
        service.add_activity("Transportation", 300.0, "", today)
        tips = service.get_recommendations()
        assert any("transportation" in t.lower() for t in tips)

    def test_high_energy_triggers_tip(self, service, today):
        # Need > 30 kg CO2 from energy: 30/0.233 ≈ 128.8 kWh
        service.add_activity("Energy", 200.0, "", today)
        tips = service.get_recommendations()
        assert any("energy" in t.lower() for t in tips)

    def test_high_water_triggers_tip(self, service, today):
        service.add_activity("Water", 600.0, "", today)
        tips = service.get_recommendations()
        assert any("water" in t.lower() for t in tips)

    def test_high_waste_triggers_tip(self, service, today):
        service.add_activity("Waste", 25.0, "", today)
        tips = service.get_recommendations()
        assert any("waste" in t.lower() for t in tips)

    def test_exceeded_goal_triggers_warning(self, service, today):
        service.add_activity("Transportation", 600.0, "", today)  # 126 kg CO2
        goal = SustainabilityGoal(50.0)
        tips = service.get_recommendations(goal=goal)
        assert any("exceeded" in t.lower() for t in tips)

    def test_no_goal_does_not_raise(self, service, today):
        service.add_activity("Transportation", 10.0, "", today)
        tips = service.get_recommendations(goal=None)
        assert isinstance(tips, list)
