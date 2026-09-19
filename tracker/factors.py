"""
Environmental impact factors for the Climate Action & Sustainability Tracker.

IMPORTANT: These are simplified, approximate values intended for
demonstration and educational purposes only.
This is NOT a scientific carbon-accounting system.

Sources of approximation:
- Transportation: average petrol car emits ~0.21 kg CO2 per km
- Energy: UK grid average ~0.233 kg CO2 per kWh (varies by country/year)
- Water: tracked as litres (pass-through, no CO2 conversion)
- Waste: tracked as kilograms (pass-through, no CO2 conversion)

To adjust the factors, edit the IMPACT_FACTORS dictionary below.
"""


class EnvironmentalFactors:
    """
    Centralised environmental constants.

    All values are class-level so they can be accessed without
    creating an instance: EnvironmentalFactors.IMPACT_FACTORS
    """

    # The four supported activity categories
    ALLOWED_CATEGORIES: tuple[str, ...] = (
        "Transportation",
        "Energy",
        "Water",
        "Waste",
    )

    # Unit automatically assigned to each category
    CATEGORY_UNITS: dict[str, str] = {
        "Transportation": "km",
        "Energy": "kWh",
        "Water": "litres",
        "Waste": "kg",
    }

    # Impact multiplier per unit for each category.
    # Transportation and Energy → kg CO2 emitted
    # Water → litres used (factor 1.0, pass-through)
    # Waste → kg generated (factor 1.0, pass-through)
    IMPACT_FACTORS: dict[str, float] = {
        "Transportation": 0.21,   # kg CO2 per km
        "Energy": 0.233,          # kg CO2 per kWh
        "Water": 1.0,             # litres per litre (pass-through)
        "Waste": 1.0,             # kg per kg (pass-through)
    }

    # Categories that contribute to carbon emissions
    CARBON_CATEGORIES: tuple[str, ...] = ("Transportation", "Energy")
