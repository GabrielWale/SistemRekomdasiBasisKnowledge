"""High-level orchestration for generating equipment recommendations."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from data.loader import load_equipment
from nlp.parser import parse_preferences
from utils.models import EquipmentKit, Preference
from utils.scoring import score_kit


@lru_cache(maxsize=1)
def _load_kits() -> List[EquipmentKit]:
    rows = load_equipment()
    return [EquipmentKit.from_row(row) for row in rows]


def recommend(preference: Preference, top_k: int = 3) -> List[dict]:
    kits = _load_kits()
    scored = [score_kit(kit, preference) for kit in kits]
    ranked = sorted(scored, key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def recommend_from_text(user_text: str, top_k: int = 3) -> List[dict]:
    preference = parse_preferences(user_text)
    if not preference.has_signals():
        raise ValueError("Deskripsi belum mencantumkan kebutuhan yang bisa dipahami. Tambahkan konteks seperti lingkungan, fokus, atau prioritas.")
    if not preference.environment:
        preference.environment = ["indoor", "outdoor"]
    return recommend(preference, top_k=top_k)
