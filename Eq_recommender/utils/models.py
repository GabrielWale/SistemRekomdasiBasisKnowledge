"""Data models shared across project modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(slots=True)
class EquipmentKit:
    name: str
    category: str
    price_band: str
    portability: str
    environment: List[str] = field(default_factory=list)
    audio_quality: str = "medium"
    stabilization: str = "medium"
    experience: str = "beginner"
    best_for: List[str] = field(default_factory=list)
    description: str = ""
    components: List[str] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: dict) -> "EquipmentKit":
        return cls(
            name=row["name"],
            category=row.get("category", "other"),
            price_band=row.get("price_band", "medium"),
            portability=row.get("portability", "medium"),
            environment=list(row.get("environment", [])),
            audio_quality=row.get("audio_quality", "medium"),
            stabilization=row.get("stabilization", "medium"),
            experience=row.get("experience", "beginner"),
            best_for=list(row.get("best_for", [])),
            description=row.get("description", ""),
            components=list(row.get("components", [])),
        )


@dataclass(slots=True)
class Preference:
    environment: List[str] = field(default_factory=list)
    budget: str = "medium"
    mobility: str = "medium"
    expertise: str = "beginner"
    focus: List[str] = field(default_factory=list)
    audio_priority: bool = False
    stabilization_priority: bool = False
    lighting: str = "neutral"  # daylight | lowlight | neutral

    def weight_for_band(self, band: str) -> float:
        order = {"low": 1, "medium": 2, "high": 3}
        return max(0.5, 1.0 - abs(order.get(self.budget, 2) - order.get(band, 2)) * 0.25)

    def has_signals(self) -> bool:
        return any(
            [
                bool(self.environment),
                bool(self.focus),
                self.audio_priority,
                self.stabilization_priority,
                self.budget != "medium",
                self.mobility != "medium",
                self.expertise != "beginner",
                self.lighting != "neutral",
            ]
        )


def normalize_tags(values: Iterable[str]) -> List[str]:
    return sorted({value.strip().lower() for value in values if value})
