"""Scoring helpers separating recommendation logic from the UI."""
from __future__ import annotations

from typing import Dict

from .models import EquipmentKit, Preference


def score_kit(kit: EquipmentKit, pref: Preference) -> Dict[str, float]:
    score = 0.0

    if pref.environment:
        overlap = len(set(pref.environment) & set(kit.environment))
        score += overlap * 1.5

        # Simple lighting bias: if user mentions daylight, prefer kits yang siap outdoor
        if pref.lighting == "daylight" and "outdoor" not in kit.environment:
            score -= 0.5
        if pref.lighting == "lowlight" and "indoor" not in kit.environment:
            score -= 0.3

    if pref.focus:
        focus_overlap = len(set(pref.focus) & set(kit.best_for))
        score += focus_overlap * 2.0

    score += pref.weight_for_band(kit.price_band)

    mobility_map = {"high": 1.0, "medium": 0.5, "low": 0.0}
    score += mobility_map.get(kit.portability, 0.5) * (1.0 if pref.mobility == "high" else 0.6)

    experience_bonus = 1.0 if kit.experience == pref.expertise else 0.5
    score += experience_bonus

    if pref.audio_priority:
        score += {"high": 1.0, "medium": 0.5}.get(kit.audio_quality, 0.0)

    if pref.stabilization_priority:
        score += {"high": 1.0, "medium": 0.5}.get(kit.stabilization, 0.0)

    return {"name": kit.name, "score": score, "kit": kit}
