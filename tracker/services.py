"""
Business logic for the Climate Action & Sustainability Tracker.

ActivityService is the single entry point for all operations.
The Streamlit UI only imports and calls this class.
"""

import datetime
from pathlib import Path

from tracker.models import Activity, SustainabilityGoal
from tracker.factors import EnvironmentalFactors
from tracker.storage import StorageManager
from tracker.exceptions import (
    InvalidAmountError,
    InvalidCategoryError,
    InvalidDateError,
)


class ActivityService:
    """
    Manages all environmental activity logic.

    Responsibilities:
    - Validate user input before creating Activity objects
    - Add activities and persist them via StorageManager
    - Aggregate totals (CO2, water, waste)
    - Calculate progress toward the user's monthly goal
    - Generate simple sustainability recommendations

    Args:
        storage: Optional StorageManager instance. If not provided,
                 the default JSON file path is used. Useful for testing.
    """

    def __init__(self, storage: StorageManager | None = None) -> None:
        self._storage: StorageManager = storage if storage is not None else StorageManager()
        self._activities: list[Activity] = self._storage.load_activities()

    # ------------------------------------------------------------------
    # Activity management
    # ------------------------------------------------------------------

    def add_activity(
        self,
        category: str,
        amount: float,
        description: str,
        date: datetime.date,
    ) -> Activity:
        """
        Validate inputs, create an Activity, and persist it.

        Args:
            category:    Must be one of EnvironmentalFactors.ALLOWED_CATEGORIES.
            amount:      Must be > 0.
            description: Optional free-text note (max 200 chars, not enforced here).
            date:        Must not be in the future.

        Returns:
            The newly created Activity.

        Raises:
            InvalidCategoryError: If category is not allowed.
            InvalidAmountError:   If amount is <= 0.
            InvalidDateError:     If date is in the future.
        """
        if category not in EnvironmentalFactors.ALLOWED_CATEGORIES:
            raise InvalidCategoryError(
                f"'{category}' is not a valid category. "
                f"Choose from: {', '.join(EnvironmentalFactors.ALLOWED_CATEGORIES)}."
            )

        if amount <= 0:
            raise InvalidAmountError(
                f"Amount must be greater than zero. Got: {amount}."
            )

        if date > datetime.date.today():
            raise InvalidDateError(
                f"Activity date cannot be in the future. Got: {date}."
            )

        activity = Activity(
            category=category,
            amount=amount,
            description=description.strip(),
            date=date,
        )
        self._activities.append(activity)
        self._storage.save_activities(self._activities)
        return activity

    def get_all_activities(self) -> list[Activity]:
        """Return a copy of all recorded activities."""
        return list(self._activities)

    def get_by_category(self, category: str) -> list[Activity]:
        """Return all activities that match the given category."""
        return [a for a in self._activities if a.category == category]

    # ------------------------------------------------------------------
    # Aggregate calculations
    # ------------------------------------------------------------------

    def total_carbon_emissions(self) -> float:
        """
        Sum CO2 impact for Transportation and Energy activities.

        Returns:
            Total kg CO2 emitted, rounded to 2 decimal places.
        """
        total = sum(
            a.impact
            for a in self._activities
            if a.category in EnvironmentalFactors.CARBON_CATEGORIES
        )
        return round(total, 2)

    def total_water_usage(self) -> float:
        """
        Sum water usage for Water activities.

        Returns:
            Total litres used, rounded to 2 decimal places.
        """
        total = sum(a.impact for a in self._activities if a.category == "Water")
        return round(total, 2)

    def total_waste_generated(self) -> float:
        """
        Sum waste for Waste activities.

        Returns:
            Total kg of waste, rounded to 2 decimal places.
        """
        total = sum(a.impact for a in self._activities if a.category == "Waste")
        return round(total, 2)

    def category_summary(self) -> dict[str, float]:
        """
        Return total impact per category.

        Returns:
            Dict mapping category name to total impact value.
            All four categories are always present (0.0 if no data).
        """
        summary: dict[str, float] = {cat: 0.0 for cat in EnvironmentalFactors.ALLOWED_CATEGORIES}
        for activity in self._activities:
            summary[activity.category] = round(summary[activity.category] + activity.impact, 4)
        return summary

    # ------------------------------------------------------------------
    # Progress toward goal
    # ------------------------------------------------------------------

    def get_progress(self, goal: SustainabilityGoal) -> tuple[float, float, float]:
        """
        Calculate how much of the monthly CO2 goal has been used.

        Args:
            goal: The user's SustainabilityGoal.

        Returns:
            A tuple of (used_co2, target_co2, percent_used) where
            percent_used is capped at 100.0.
        """
        used = self.total_carbon_emissions()
        target = goal.monthly_target_kg_co2
        percent = min(round((used / target) * 100, 1), 100.0)
        return used, target, percent

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def get_recommendations(self, goal: SustainabilityGoal | None = None) -> list[str]:
        """
        Generate simple rule-based sustainability tips.

        Rules:
        - No activities yet → prompt to start logging
        - Transportation CO2 > 50 kg → carpooling / public transport tip
        - Energy CO2 > 30 kg → reduce appliance usage tip
        - Water usage > 500 litres → shorter showers / fix leaks tip
        - Waste > 20 kg → composting / reduce packaging tip
        - Total CO2 > goal target → exceeded-goal warning

        Args:
            goal: Optional SustainabilityGoal. If provided, goal-exceeded
                  check is included.

        Returns:
            A list of recommendation strings.
        """
        tips: list[str] = []

        if not self._activities:
            tips.append(
                "🌱 No activities recorded yet. Start logging your activities "
                "to see your environmental impact and get personalised tips."
            )
            return tips

        summary = self.category_summary()

        transport_co2 = summary.get("Transportation", 0.0)
        energy_co2 = summary.get("Energy", 0.0)
        water_litres = summary.get("Water", 0.0)
        waste_kg = summary.get("Waste", 0.0)

        if transport_co2 > 50:
            tips.append(
                f"🚗 Your transportation emissions are {transport_co2:.1f} kg CO₂. "
                "Consider carpooling, using public transport, or cycling for short trips."
            )

        if energy_co2 > 30:
            tips.append(
                f"⚡ Your energy usage has produced {energy_co2:.1f} kg CO₂. "
                "Try turning off appliances when not in use, using energy-efficient bulbs, "
                "or lowering your thermostat by 1–2°C."
            )

        if water_litres > 500:
            tips.append(
                f"💧 You have used {water_litres:.1f} litres of water. "
                "Shorter showers, fixing dripping taps, and using a dishwasher on full loads "
                "can significantly reduce water consumption."
            )

        if waste_kg > 20:
            tips.append(
                f"🗑️ You have generated {waste_kg:.1f} kg of waste. "
                "Consider composting organic waste, buying items with less packaging, "
                "and recycling more."
            )

        if goal is not None:
            used_co2 = self.total_carbon_emissions()
            if used_co2 > goal.monthly_target_kg_co2:
                tips.append(
                    f"⚠️ You have exceeded your monthly CO₂ goal of "
                    f"{goal.monthly_target_kg_co2:.1f} kg "
                    f"(currently at {used_co2:.1f} kg). "
                    "Focus on reducing transportation and energy use for the rest of the month."
                )

        if not tips:
            tips.append(
                "✅ Great work! You are within all recommended thresholds. "
                "Keep logging your activities to stay on track."
            )

        return tips
