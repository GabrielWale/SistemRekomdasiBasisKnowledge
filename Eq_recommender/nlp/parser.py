"""Lightweight keyword-based NLP parser producing structured preferences."""
from __future__ import annotations

from typing import Iterable, List

from utils.models import Preference, normalize_tags

STOPWORDS = {
    "dan", "yang", "untuk", "dengan", "di", "ke", "dari", "atau", "pada", "ini",
    "itu", "saat", "karena", "dalam", "agar", "bagi", "guna", "serta", "ada", "akan",
    "tidak", "ya", "kok", "lah", "kah", "nih", "deh", "dong", "banget", "aja", "juga",
    "misalnya", "contoh", "seperti", "jadi", "kalau", "bila", "sudah", "belum",
    "saya", "aku", "kamu", "ingin", "pengen", "membuat", "buat", "konten", "kontennya", "kontenmu",
    "hari", "waktu",
}

# Canonical keyword mapping
CANON = {
    "outdoor": {"outdoor", "luar", "ruangan", "jalan", "jalan2", "travel", "trip", "liburan", "alam", "nature", "siang", "terang", "matahari", "cerah"},
    "indoor": {"indoor", "studio", "ruangan", "setup"},
    "hybrid": {"hybrid", "flex"},
    "travel": {"travel", "jalan", "trip", "liburan", "vlog"},
    "podcast": {"podcast", "audio", "talk", "talking", "head"},
    "interview": {"interview", "wawancara"},
    "action": {"action", "sport", "olahraga"},
}

BUDGET_KEYWORDS = {
    "low": {"murah", "hemat", "budget", "entry"},
    "high": {"mahal", "premium", "pro"},
}

MOBILITY_KEYWORDS = {
    "high": {"ringan", "travel", "portable", "mobile"},
    "low": {"studio", "tetap", "statis"},
}

EXPERTISE_KEYWORDS = {
    "beginner": {"pemula", "beginner", "baru"},
    "intermediate": {"menengah", "intermediate"},
    "pro": {"profesional", "expert", "pro"},
}

AUDIO_FLAGS = {"audio", "mic", "suara", "podcast"}
STAB_FLAGS = {"stabil", "gimbal", "steady", "aksi", "action"}

DAYLIGHT_TOKENS = {"siang", "terang", "matahari", "cerah"}
LOWLIGHT_TOKENS = {"malam", "gelap", "lowlight"}


def _tokenize(text: str) -> List[str]:
    raw = text.lower()
    tokens: List[str] = []
    for token in raw.replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").split():
        clean = "".join(ch for ch in token if ch.isalnum())
        if clean:
            tokens.append(clean)
    return [t for t in tokens if t and t not in STOPWORDS]


def _contains_any(tokens: Iterable[str], keywords: Iterable[str]) -> bool:
    token_set = set(tokens)
    return bool(token_set & set(keywords))


def _canonical_hits(tokens: Iterable[str], mapping: dict) -> List[str]:
    hits: List[str] = []
    for canon, variants in mapping.items():
        if _contains_any(tokens, variants):
            hits.append(canon)
    return hits


def parse_preferences(text: str) -> Preference:
    tokens = _tokenize(text)
    pref = Preference()

    env_hits = _canonical_hits(tokens, {k: v for k, v in CANON.items() if k in {"outdoor", "indoor", "hybrid"}})
    focus_hits = _canonical_hits(tokens, {k: v for k, v in CANON.items() if k not in {"outdoor", "indoor", "hybrid"}})

    pref.environment.extend(env_hits)
    pref.focus.extend(focus_hits)

    for label, words in BUDGET_KEYWORDS.items():
        if _contains_any(tokens, words):
            pref.budget = label

    for label, words in MOBILITY_KEYWORDS.items():
        if _contains_any(tokens, words):
            pref.mobility = label

    for label, words in EXPERTISE_KEYWORDS.items():
        if _contains_any(tokens, words):
            pref.expertise = label

    pref.audio_priority = _contains_any(tokens, AUDIO_FLAGS)
    pref.stabilization_priority = _contains_any(tokens, STAB_FLAGS)

    # Lighting cue to bias away from low-light gear for daytime queries
    if _contains_any(tokens, DAYLIGHT_TOKENS):
        pref.lighting = "daylight"
    elif _contains_any(tokens, LOWLIGHT_TOKENS):
        pref.lighting = "lowlight"

    pref.environment = normalize_tags(pref.environment)
    pref.focus = normalize_tags(pref.focus)
    return pref
