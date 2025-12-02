"""Utilities for loading structured equipment data."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import csv

DATA_DIR = Path(__file__).resolve().parent
DATA_FILE = DATA_DIR / "equipment_data.csv"


class DataLoadError(RuntimeError):
    """Raised when equipment data cannot be loaded."""


def _split_tags(raw: str) -> List[str]:
    return [token.strip().lower() for token in raw.split(";") if token.strip()]


def load_equipment(path: Path | None = None) -> List[dict]:
    target = path or DATA_FILE
    if not target.exists():
        raise DataLoadError(f"Equipment data file not found: {target}")

    records: List[dict] = []
    with target.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row["environment"] = _split_tags(row.get("environment", ""))
            row["best_for"] = _split_tags(row.get("best_for", ""))
            row["components"] = [
                component.strip() for component in row.get("components", "").split("|") if component.strip()
            ]
            records.append(row)
    if not records:
        raise DataLoadError(f"No equipment entries found in {target}")
    return records
