"""Lightweight keyword-based NLP parser producing structured preferences."""
from __future__ import annotations

import re
from typing import Iterable

from utils.models import Preference, normalize_tags

ENVIRONMENT_KEYWORDS = {
    "indoor": {"studio", "indoor", "ruangan"},
    "outdoor": {"outdoor", "luar", "travel"},
    "hybrid": {"hybrid", "flex"},
}

FOCUS_KEYWORDS = {
    "podcast": {"podcast", "audio", "talk"},
    "travel": {"travel", "jalan", "trip"},
    "studio": {"studio", "setup"},
    "interview": {"interview", "wawancara"},
    "action": {"action", "sport"},
}

BUDGET_KEYWORDS = {
    "low": {"murah", "hemat", "budget", "entry"},
    "high": {"mahal", "premium", "pro"},
}

MOBILITY_KEYWORDS = {
    "high": {"ringan", "travel", "portable"},
    "low": {"studio", "tetap"},
}

EXPERTISE_KEYWORDS = {
    "beginner": {"pemula", "beginner", "baru"},
    "intermediate": {"menengah", "intermediate"},
    "pro": {"profesional", "expert", "pro"},
}

AUDIO_FLAGS = {"audio", "mic", "suara"}
STAB_FLAGS = {"stabil", "gimbal", "steady"}


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    return any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords)


def parse_preferences(text: str) -> Preference:
    lowered = text.lower()
    pref = Preference()

    for label, words in ENVIRONMENT_KEYWORDS.items():
        if _contains_any(lowered, words):
            pref.environment.append(label)

    for label, words in FOCUS_KEYWORDS.items():
        if _contains_any(lowered, words):
            pref.focus.append(label)

    for label, words in BUDGET_KEYWORDS.items():
        if _contains_any(lowered, words):
            pref.budget = label

    for label, words in MOBILITY_KEYWORDS.items():
        if _contains_any(lowered, words):
            pref.mobility = label

    for label, words in EXPERTISE_KEYWORDS.items():
        if _contains_any(lowered, words):
            pref.expertise = label

    pref.audio_priority = _contains_any(lowered, AUDIO_FLAGS)
    pref.stabilization_priority = _contains_any(lowered, STAB_FLAGS)

    pref.environment = normalize_tags(pref.environment)
    pref.focus = normalize_tags(pref.focus)
    return pref
