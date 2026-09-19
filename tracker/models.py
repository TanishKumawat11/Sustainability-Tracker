"""
Data models for the Climate Action & Sustainability Tracker.

Contains:
- Activity: represents a single recorded environmental event
- SustainabilityGoal: holds the user's monthly CO2 target
"""

import uuid
import datetime
from dataclasses import dataclass, field
from typing import Any

from tracker.factors import EnvironmentalFactors
from tracker.exceptions import InvalidGoalError


@dataclass
class Activity:
    """
    Represents a single recorded environmental activity.

    The `id`, `unit`, and `impact` fields are set automatically
    in __post_init__ — the caller only needs to supply category,
    amount, description, and date.

    Attributes:
        category:    One of Transportation, Energy, Water, Waste.
        amount:      Quantity in the category's unit (must be > 0).
        description: Optional short note about the activity.
        date:        The date the activity occurred.
        id:          Auto-generated UUID string (unique identifier).
        unit:        Auto-assigned from EnvironmentalFactors.CATEGORY_UNITS.
        impact:      Calculated impact value (CO2 kg, litres, or kg waste).
    """

    category: str
    amount: float
    description: str
    date: datetime.date

    # These are set automatically in __post_init__
    id: str = field(default="", init=False)
    unit: str = field(default="", init=False)
    impact: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        """Auto-assign id, unit, and impact after the dataclass is created."""
        self.id = str(uuid.uuid4())
        self.unit = EnvironmentalFactors.CATEGORY_UNITS[self.category]
        self.impact = round(self.amount * EnvironmentalFactors.IMPACT_FACTORS[self.category], 4)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this Activity to a plain dictionary for JSON serialisation.

        The date is stored as an ISO 8601 string (YYYY-MM-DD).
        """
        return {
            "id": self.id,
            "category": self.category,
            "amount": self.amount,
            "unit": self.unit,
            "description": self.description,
            "date": self.date.isoformat(),
            "impact": self.impact,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Activity":
        """
        Reconstruct an Activity from a stored dictionary.

        Args:
            data: A dict as produced by to_dict().

        Returns:
            A fully initialised Activity instance.
        """
        activity = cls(
            category=data["category"],
            amount=data["amount"],
            description=data.get("description", ""),
            date=datetime.date.fromisoformat(data["date"]),
        )
        # Restore the persisted id and impact (override the auto-generated ones)
        activity.id = data["id"]
        activity.impact = data["impact"]
        return activity

    def __str__(self) -> str:
        return (
            f"{self.date} | {self.category} | {self.amount} {self.unit} "
            f"| impact: {self.impact} | {self.description}"
        )


class SustainabilityGoal:
    """
    Holds the user's monthly sustainability target.

    The target is expressed in kg CO2 — the user aims to stay
    below this value for the month.

    Args:
        monthly_target_kg_co2: Target CO2 emissions in kg. Must be > 0.

    Raises:
        InvalidGoalError: If the target is zero or negative.
    """

    def __init__(self, monthly_target_kg_co2: float) -> None:
        if monthly_target_kg_co2 <= 0:
            raise InvalidGoalError()
        self.monthly_target_kg_co2: float = monthly_target_kg_co2

    def __str__(self) -> str:
        return f"Monthly CO\u2082 target: {self.monthly_target_kg_co2} kg"
