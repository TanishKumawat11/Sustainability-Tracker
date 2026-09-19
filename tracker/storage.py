"""
JSON persistence for the Climate Action & Sustainability Tracker.

StorageManager handles all file I/O so the rest of the application
never deals with raw JSON reading or writing.
"""

import json
from pathlib import Path

from tracker.models import Activity


class StorageManager:
    """
    Loads and saves Activity records to a JSON file.

    The file stores a JSON array where each element is a dict
    produced by Activity.to_dict().

    Args:
        file_path: Path to the JSON file. Defaults to data/activities.json
                   relative to the project root.
    """

    DEFAULT_PATH = Path(__file__).parent.parent / "data" / "activities.json"

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path: Path = file_path if file_path is not None else self.DEFAULT_PATH
        # Ensure the parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_activities(self) -> list[Activity]:
        """
        Read activities from the JSON file.

        Returns an empty list if the file does not exist, is empty,
        or contains invalid JSON — so the app never crashes on startup.

        Returns:
            A list of Activity objects, or [] on any read error.
        """
        try:
            text = self.file_path.read_text(encoding="utf-8").strip()
            if not text:
                return []
            records: list[dict] = json.loads(text)
            return [Activity.from_dict(record) for record in records]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            # Corrupted file — return empty rather than crashing
            return []

    def save_activities(self, activities: list[Activity]) -> None:
        """
        Write the full list of activities to the JSON file.

        The entire file is overwritten on every save (acceptable
        for a small personal tracker with few records).

        Args:
            activities: The current in-memory list of Activity objects.
        """
        records = [activity.to_dict() for activity in activities]
        self.file_path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
