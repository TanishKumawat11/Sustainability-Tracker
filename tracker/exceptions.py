"""
Custom exception classes for the Climate Action & Sustainability Tracker.

All exceptions extend ValueError so they can be caught generically
with `except ValueError` when needed.
"""


class InvalidAmountError(ValueError):
    """Raised when an activity amount is zero or negative."""

    def __init__(self, message: str = "Amount must be greater than zero.") -> None:
        super().__init__(message)


class InvalidCategoryError(ValueError):
    """Raised when a category is not in the list of allowed categories."""

    def __init__(self, message: str = "Category must be one of: Transportation, Energy, Water, Waste.") -> None:
        super().__init__(message)


class InvalidDateError(ValueError):
    """Raised when an activity date is set in the future."""

    def __init__(self, message: str = "Activity date cannot be in the future.") -> None:
        super().__init__(message)


class InvalidGoalError(ValueError):
    """Raised when a sustainability goal target is zero or negative."""

    def __init__(self, message: str = "Monthly CO\u2082 target must be greater than zero.") -> None:
        super().__init__(message)
