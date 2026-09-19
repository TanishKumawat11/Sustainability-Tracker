# Climate Action & Sustainability Tracker — Implementation Plan

## Top-Level Overview

**Goal:** Build a small, beginner-friendly Climate Action & Sustainability Tracker using Python and Streamlit.

**Scope:** A single-user desktop web app that allows recording of environmental activities, calculates simplified impact metrics (CO₂, water, waste), tracks progress toward a monthly sustainability goal, and shows basic recommendations.

**Approach:**
- Three Python modules: a data model, a service layer, and a storage module
- One Streamlit UI entry point (`app.py`)
- JSON file for persistence (`data/activities.json`)
- Custom exceptions in a dedicated module
- Simple predefined environmental factors (not scientifically precise)
- Unit tests for the model and service layers

**Non-goals:** Multi-user support, authentication, scientific carbon accounting, activity editing/deletion.

---

## Project Architecture

```
sustainability-tracker/
│
├── app.py                  # Streamlit UI — entry point
├── requirements.txt        # streamlit, pytest
│
├── tracker/
│   ├── __init__.py
│   ├── models.py           # Activity dataclass + SustainabilityGoal
│   ├── factors.py          # Predefined environmental constants
│   ├── exceptions.py       # Custom exception classes
│   ├── services.py         # ActivityService — all business logic
│   └── storage.py          # JSON read/write helpers
│
├── data/
│   └── activities.json     # Persisted activity records
│
└── tests/
    ├── test_models.py
    ├── test_services.py
    └── test_storage.py
```

### Component Communication

```
app.py (Streamlit UI)
    |
    |-- calls --> ActivityService (services.py)
                      |
                      |-- reads/writes --> StorageManager (storage.py)
                      |                         |
                      |                         +--> data/activities.json
                      |
                      |-- uses --> Activity, SustainabilityGoal (models.py)
                      |
                      |-- uses --> EnvironmentalFactors (factors.py)
                      |
                      |-- raises --> Custom Exceptions (exceptions.py)
```

The UI layer never reads the JSON file directly and never performs calculations — it only calls the service layer and renders results.

---

## Environmental Factors (Simplified Assumptions)

> These are approximate values for demonstration purposes only.
> This is NOT a scientific carbon-accounting system.

| Category       | Unit    | Impact Factor         | What It Produces      |
|----------------|---------|----------------------|-----------------------|
| Transportation | km      | 0.21 kg CO₂ per km   | Carbon emissions      |
| Energy         | kWh     | 0.233 kg CO₂ per kWh | Carbon emissions      |
| Water          | litres  | 1.0 litre per litre  | Water usage (pass-through) |
| Waste          | kg      | 1.0 kg per kg        | Waste generated (pass-through) |

Carbon emissions are calculated for Transportation and Energy only.
Water usage is totalled from Water category entries only.
Waste is totalled from Waste category entries only.

---

## Data Model

### Activity
Represents a single recorded environmental event.

| Field         | Type           | Constraints                              |
|---------------|----------------|------------------------------------------|
| `id`          | `str` (UUID)   | Auto-generated, never user-supplied      |
| `category`    | `str`          | One of: Transportation, Energy, Water, Waste |
| `amount`      | `float`        | Must be > 0                              |
| `unit`        | `str`          | Auto-assigned based on category          |
| `description` | `str`          | Optional, max 200 chars                  |
| `date`        | `datetime.date`| Cannot be in the future                  |
| `impact`      | `float`        | Calculated at creation time using factors|

### SustainabilityGoal
Holds the user's monthly CO₂ target.

| Field                  | Type    | Constraints |
|------------------------|---------|-------------|
| `monthly_target_kg_co2`| `float` | Must be > 0 |

### JSON Record Shape (per activity)
```json
{
  "id": "uuid-string",
  "category": "Transportation",
  "amount": 25.0,
  "unit": "km",
  "description": "Drove to work",
  "date": "2025-07-01",
  "impact": 5.25
}
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding
**Status:** [ ] pending

**Intent:** Create the folder structure, empty module files, and `requirements.txt` so that all subsequent sub-tasks have a clean place to work.

**Expected Outcomes:**
- `sustainability-tracker/` directory exists with all folders and empty `__init__.py` files
- `requirements.txt` lists `streamlit` and `pytest`
- `data/activities.json` exists as an empty JSON array `[]`
- `app.py` exists as an empty placeholder

**Todo List:**
1. Create `tracker/` package folder with `__init__.py`
2. Create empty module files: `models.py`, `factors.py`, `exceptions.py`, `services.py`, `storage.py`
3. Create `data/` folder with `activities.json` initialised to `[]`
4. Create `tests/` folder with empty test files
5. Create `requirements.txt` with `streamlit` and `pytest`
6. Create placeholder `app.py`

**Relevant Context:** No existing codebase — greenfield project.

---

### Sub-Task 2 — Exceptions Module
**Status:** [ ] pending

**Intent:** Define all custom exception classes in one place so the rest of the application can import and raise them cleanly.

**Expected Outcomes:**
- `tracker/exceptions.py` contains four custom exception classes
- Each exception has a descriptive default message

**Todo List:**
1. Define `InvalidAmountError(ValueError)` — raised when amount <= 0
2. Define `InvalidCategoryError(ValueError)` — raised when category is not in the allowed list
3. Define `InvalidDateError(ValueError)` — raised when date is in the future
4. Define `InvalidGoalError(ValueError)` — raised when monthly target <= 0

**Relevant Context:** All exceptions extend `ValueError` so they can be caught generically if needed.

---

### Sub-Task 3 — Environmental Factors Module
**Status:** [ ] pending

**Intent:** Centralise all predefined environmental constants so they are easy to find and update in one place.

**Expected Outcomes:**
- `tracker/factors.py` contains an `EnvironmentalFactors` class with class-level constants
- `CATEGORY_UNITS` dict maps each category to its required unit
- `ALLOWED_CATEGORIES` list/tuple enumerates valid categories
- `IMPACT_FACTORS` dict maps each category to its numeric multiplier

**Todo List:**
1. Define `ALLOWED_CATEGORIES` as a tuple of four strings
2. Define `CATEGORY_UNITS` dict mapping each category to its unit string
3. Define `IMPACT_FACTORS` dict mapping each category to its float multiplier
4. Add a module-level docstring clearly stating these are simplified assumptions

**Relevant Context:** See environmental factors table above.

---

### Sub-Task 4 — Data Models
**Status:** [ ] pending

**Intent:** Define the `Activity` dataclass and `SustainabilityGoal` class that the entire application revolves around.

**Expected Outcomes:**
- `tracker/models.py` contains `Activity` and `SustainabilityGoal`
- `Activity` auto-generates its `id` and calculates `impact` on creation
- `Activity` exposes a `to_dict()` method and a `from_dict()` classmethod for JSON serialisation
- `SustainabilityGoal` validates its target on construction

**Todo List:**
1. Import `uuid`, `datetime`, `dataclasses`, and local modules
2. Define `Activity` as a `@dataclass` with all fields from the data model table
3. In `Activity.__post_init__()`, auto-assign `id` (UUID) and `unit` (from `CATEGORY_UNITS`), and calculate `impact`
4. Add `Activity.to_dict()` — returns a plain dict suitable for JSON serialisation (date as ISO string)
5. Add `Activity.from_dict(data)` classmethod — reconstructs an `Activity` from a stored dict
6. Define `SustainabilityGoal` with `monthly_target_kg_co2` field, validate > 0 in `__init__`

**Relevant Context:**
- `Activity` should NOT perform validation — that is the service layer's job
- `impact` is computed as `amount * IMPACT_FACTORS[category]`

---

### Sub-Task 5 — Storage Module
**Status:** [ ] pending

**Intent:** Provide simple JSON file read/write helpers so the service layer never handles raw file I/O directly.

**Expected Outcomes:**
- `tracker/storage.py` contains `StorageManager` class
- `load_activities()` reads `data/activities.json` and returns a list of `Activity` objects
- `save_activities(activities)` writes the full list back to JSON
- If the file does not exist or is empty, `load_activities()` returns an empty list safely

**Todo List:**
1. Define `StorageManager` with a configurable `file_path` (defaults to `data/activities.json`)
2. Implement `load_activities()` — reads JSON, deserialises each record using `Activity.from_dict()`
3. Implement `save_activities(activities: list[Activity])` — serialises each `Activity` using `to_dict()` and writes the full list
4. Handle missing file and empty file edge cases gracefully (return `[]`)

**Relevant Context:**
- Uses Python's built-in `json` and `pathlib` modules — no third-party dependencies
- The file path should be relative to the project root

---

### Sub-Task 6 — Service Layer
**Status:** [ ] pending

**Intent:** Implement all business logic in `ActivityService` — validation, activity creation, aggregation, progress calculation, and recommendations. The UI calls only this layer.

**Expected Outcomes:**
- `tracker/services.py` contains `ActivityService` class
- All input validation is performed here before creating an `Activity`
- Aggregate methods return clean numeric values
- Recommendation logic is simple and rule-based

**Todo List:**
1. Define `ActivityService.__init__()` — creates a `StorageManager` and loads activities into memory
2. Implement `add_activity(category, amount, description, date)`:
   - Validate category against `ALLOWED_CATEGORIES` → raise `InvalidCategoryError`
   - Validate amount > 0 → raise `InvalidAmountError`
   - Validate date is not in the future → raise `InvalidDateError`
   - Create `Activity`, append to in-memory list, persist via `StorageManager`
3. Implement `get_all_activities()` — returns the in-memory list
4. Implement `get_by_category(category)` — filters the list
5. Implement `total_carbon_emissions()` — sums `impact` for Transportation + Energy
6. Implement `total_water_usage()` — sums `impact` for Water
7. Implement `total_waste_generated()` — sums `impact` for Waste
8. Implement `category_summary()` — returns `{category: total_impact}` dict for all four categories
9. Implement `get_progress(goal: SustainabilityGoal)` — returns `(used_co2, target_co2, percent)` tuple
10. Implement `get_recommendations(goal: SustainabilityGoal)` — returns a list of tip strings using simple if/threshold rules

**Recommendation Rules (simple thresholds):**
- Transportation impact > 50 kg CO₂ → suggest carpooling / public transport
- Energy impact > 30 kg CO₂ → suggest reducing appliance usage
- Water usage > 500 litres → suggest shorter showers / fixing leaks
- Waste > 20 kg → suggest composting / reducing packaging
- Total CO₂ > goal target → warn the user they have exceeded their goal
- No activities recorded → prompt the user to start logging

**Relevant Context:**
- `ActivityService` is the ONLY class that `app.py` imports from `tracker`
- `StorageManager` is an implementation detail hidden inside the service

---

### Sub-Task 7 — Streamlit UI
**Status:** [ ] pending

**Intent:** Build the user-facing interface in `app.py` using Streamlit. The UI is thin — it collects input, calls the service, and renders results.

**Expected Outcomes:**
- `app.py` has a sidebar for setting the monthly goal
- Four tabs: Add Activity, View Activities, Impact Summary, Recommendations
- All user errors are displayed as `st.error()` messages — no crashes
- Progress bar shows CO₂ used vs. goal
- Activities are displayed in a `st.dataframe()` table

**Todo List:**
1. Initialise `st.session_state` with an `ActivityService` instance on first load
2. Build sidebar: number input for monthly CO₂ goal → creates/updates `SustainabilityGoal`
3. Build **Add Activity** tab:
   - `st.selectbox` for category (drives unit display)
   - `st.number_input` for amount
   - `st.text_input` for description (optional)
   - `st.date_input` for date (default today)
   - On submit: call `service.add_activity()`, catch custom exceptions, show success or error
4. Build **View Activities** tab:
   - Show `st.dataframe()` of all activities
   - Show "No activities recorded yet" if list is empty
5. Build **Impact Summary** tab:
   - Show total CO₂, total water, total waste as `st.metric()` cards
   - Show category breakdown as a simple `st.bar_chart()` or table
   - Show progress bar with `st.progress()` and a caption
6. Build **Recommendations** tab:
   - Call `service.get_recommendations()` and render each tip as a bullet point
7. Ensure the app handles the "goal not set yet" state gracefully

**Relevant Context:**
- `st.session_state` is used instead of re-instantiating the service on every rerun
- The service layer already persists to JSON — the UI does not need to call storage directly

---

### Sub-Task 8 — Unit Tests
**Status:** [ ] pending

**Intent:** Write focused unit tests for the model, service, and storage layers to verify correctness of calculations, validation, and serialisation.

**Expected Outcomes:**
- `tests/test_models.py` covers Activity creation, impact calculation, to_dict/from_dict
- `tests/test_services.py` covers validation errors, aggregation methods, recommendations
- `tests/test_storage.py` covers load/save round-trip using a temporary file
- All tests pass with `pytest`

**Todo List:**
1. `test_models.py`:
   - Test that `Activity` calculates `impact` correctly for each category
   - Test that `to_dict()` and `from_dict()` round-trip correctly
   - Test that unit is auto-assigned from category
2. `test_services.py`:
   - Test `add_activity()` raises `InvalidAmountError` for amount <= 0
   - Test `add_activity()` raises `InvalidCategoryError` for unknown category
   - Test `add_activity()` raises `InvalidDateError` for a future date
   - Test `total_carbon_emissions()` sums Transportation + Energy only
   - Test `total_water_usage()` sums Water only
   - Test `total_waste_generated()` sums Waste only
   - Test `get_progress()` returns correct percentage
   - Test `get_recommendations()` returns expected tips for seeded data
3. `test_storage.py`:
   - Test `save_activities()` + `load_activities()` round-trip with a temp JSON file
   - Test `load_activities()` returns `[]` when file does not exist

**Relevant Context:**
- Use `pytest` and Python's `tempfile` module for the storage tests
- No mocking needed — tests call real code with controlled inputs

---

## Input Validation Strategy

Validation is centralised in `ActivityService.add_activity()` only. Models do not validate. The UI catches exceptions and shows them as `st.error()` messages.

| Rule | Where Enforced | Exception |
|---|---|---|
| amount > 0 | `ActivityService` | `InvalidAmountError` |
| category in allowed list | `ActivityService` | `InvalidCategoryError` |
| date not in future | `ActivityService` | `InvalidDateError` |
| goal > 0 | `SustainabilityGoal.__init__` | `InvalidGoalError` |

---

## Exception Handling Strategy

| Layer | Behaviour |
|---|---|
| `models.py` | Raises `InvalidGoalError` only for goal validation |
| `services.py` | Raises `InvalidAmountError`, `InvalidCategoryError`, `InvalidDateError` |
| `storage.py` | Catches `FileNotFoundError` and `json.JSONDecodeError` internally; returns `[]` |
| `app.py` | Wraps all service calls in `try/except`; displays `st.error()` — never crashes |

---

## Main User Flows

### Flow 1 — Set Monthly Goal
Sidebar → enter target kg CO₂ → `SustainabilityGoal` created → stored in `session_state`

### Flow 2 — Add an Activity
Add Activity tab → fill form → submit → `service.add_activity()` → validate → create `Activity` → save to JSON → success message

### Flow 3 — View Activities
View Activities tab → `service.get_all_activities()` → render as dataframe

### Flow 4 — Check Impact
Impact Summary tab → call `total_carbon_emissions()`, `total_water_usage()`, `total_waste_generated()`, `category_summary()`, `get_progress()` → render metrics + progress bar

### Flow 5 — Get Recommendations
Recommendations tab → `service.get_recommendations(goal)` → render tips as list

---

## Implementation Checklist (for AI coding agent)

- [ ] Sub-Task 1: Create project folder structure, empty modules, `requirements.txt`, `data/activities.json`
- [ ] Sub-Task 2: Implement `tracker/exceptions.py` with four custom exception classes
- [ ] Sub-Task 3: Implement `tracker/factors.py` with `EnvironmentalFactors` constants
- [ ] Sub-Task 4: Implement `tracker/models.py` with `Activity` dataclass and `SustainabilityGoal`
- [ ] Sub-Task 5: Implement `tracker/storage.py` with `StorageManager` load/save methods
- [ ] Sub-Task 6: Implement `tracker/services.py` with `ActivityService` and all business logic
- [ ] Sub-Task 7: Implement `app.py` Streamlit UI with sidebar, four tabs, and error handling
- [ ] Sub-Task 8: Write unit tests in `tests/` and verify all pass with `pytest`
