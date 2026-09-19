"""
Unit tests for tracker/storage.py

Tests:
- save_activities() + load_activities() round-trip
- load_activities() returns [] when file does not exist
- load_activities() returns [] when file is empty
- load_activities() returns [] when file contains invalid JSON
"""

import datetime
import json
from pathlib import Path

import pytest

from tracker.models import Activity
from tracker.storage import StorageManager


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_activity(category: str, amount: float) -> Activity:
    return Activity(
        category=category,
        amount=amount,
        description="storage test",
        date=datetime.date(2025, 6, 1),
    )


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

class TestStorageRoundTrip:
    def test_save_and_load_single_activity(self, tmp_path: Path):
        json_file = tmp_path / "test.json"
        storage = StorageManager(file_path=json_file)

        original = make_activity("Transportation", 25.0)
        storage.save_activities([original])

        loaded = storage.load_activities()
        assert len(loaded) == 1
        assert loaded[0].id == original.id
        assert loaded[0].category == original.category
        assert loaded[0].amount == original.amount
        assert loaded[0].unit == original.unit
        assert loaded[0].impact == original.impact
        assert loaded[0].date == original.date

    def test_save_and_load_multiple_activities(self, tmp_path: Path):
        json_file = tmp_path / "test.json"
        storage = StorageManager(file_path=json_file)

        activities = [
            make_activity("Transportation", 10.0),
            make_activity("Energy", 30.0),
            make_activity("Water", 150.0),
            make_activity("Waste", 5.0),
        ]
        storage.save_activities(activities)

        loaded = storage.load_activities()
        assert len(loaded) == 4
        ids_original = [a.id for a in activities]
        ids_loaded = [a.id for a in loaded]
        assert ids_original == ids_loaded

    def test_save_overwrites_previous_content(self, tmp_path: Path):
        json_file = tmp_path / "test.json"
        storage = StorageManager(file_path=json_file)

        storage.save_activities([make_activity("Water", 100.0)])
        storage.save_activities([make_activity("Waste", 5.0)])  # overwrite

        loaded = storage.load_activities()
        assert len(loaded) == 1
        assert loaded[0].category == "Waste"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestStorageEdgeCases:
    def test_load_when_file_does_not_exist(self, tmp_path: Path):
        json_file = tmp_path / "nonexistent.json"
        storage = StorageManager(file_path=json_file)
        result = storage.load_activities()
        assert result == []

    def test_load_when_file_is_empty(self, tmp_path: Path):
        json_file = tmp_path / "empty.json"
        json_file.write_text("", encoding="utf-8")
        storage = StorageManager(file_path=json_file)
        result = storage.load_activities()
        assert result == []

    def test_load_when_file_contains_empty_array(self, tmp_path: Path):
        json_file = tmp_path / "empty_array.json"
        json_file.write_text("[]", encoding="utf-8")
        storage = StorageManager(file_path=json_file)
        result = storage.load_activities()
        assert result == []

    def test_load_when_file_has_invalid_json(self, tmp_path: Path):
        json_file = tmp_path / "corrupt.json"
        json_file.write_text("not valid json {{", encoding="utf-8")
        storage = StorageManager(file_path=json_file)
        result = storage.load_activities()
        assert result == []

    def test_save_creates_parent_directory(self, tmp_path: Path):
        json_file = tmp_path / "subdir" / "deep" / "activities.json"
        storage = StorageManager(file_path=json_file)
        storage.save_activities([make_activity("Energy", 10.0)])
        assert json_file.exists()

    def test_json_file_is_human_readable(self, tmp_path: Path):
        """Saved file should use indented JSON (not a single line)."""
        json_file = tmp_path / "test.json"
        storage = StorageManager(file_path=json_file)
        storage.save_activities([make_activity("Waste", 3.0)])
        content = json_file.read_text(encoding="utf-8")
        # indented JSON has newlines
        assert "\n" in content
