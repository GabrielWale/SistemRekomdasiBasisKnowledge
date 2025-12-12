"""Lightweight keyword-based NLP parser producing structured preferences."""
from __future__ import annotations

from typing import Iterable, List

from utils.models import Preference, normalize_tags

# ============================================================
# STOPWORDS ditambah dan dibersihkan
# ============================================================
STOPWORDS = {
    "dan","yang","untuk","dengan","di","ke","dari","atau","pada","ini","itu",
    "saat","karena","dalam","agar","bagi","guna","serta","ada","akan",
    "tidak","ya","kok","lah","kah","nih","deh","dong","banget","aja","juga",
    "misalnya","contoh","seperti","jadi","kalau","bila","sudah","belum",
    "saya","aku","kamu","ingin","pengen","membuat","buat","konten",
    "kontennya","kontenmu","hari","waktu","di", "yang",
}

# ============================================================
# CANONICAL KEYWORDS VERSI UPGRADE 
# ============================================================
CANON = {
    # ░░░ ENVIRONMENT ░░░
    "outdoor": {
        "outdoor","luar","alam","nature","ruangan","siang","terang","cerah",
        "matahari","sunny","sunlight",
        "jalan","jalan2","travel","trip","liburan","explore","petualangan",
        "pantai","gunung","pegunungan","bukit","hiking","camping","adventure"
    },
    "indoor": {
        "indoor","studio","ruangan","setup","kelas","dalam","indoorstudio",
        "podcastroom"
    },
    "hybrid": {"hybrid","flex","campuran"},

    #CONTENT TYPE
    "travel": {
        "travel","liburan","jalan","trip","vlog","backpacking","keliling",
        "solo","adventure","hiking","explore"
    },
    "podcast": {
        "podcast","audio","mic","suara","record","talk","talking","voiceover"
    },
    "interview": {
        "interview","wawancara","narasumber","bicara","QnA"
    },
    "action": {
        "action","aksi","sport","olahraga","extreme","lari","balap","skate"
    },
    "cinematic": {
        "cinematic","sinematik","bokeh","estetik","blur","slowmo","film"
    },
    "tutorial": {
        "tutorial","review","unboxing","howto","demo"
    },
    "lowlight": {
        "lowlight","malam","gelap","noise","noisy","night"
    },
}

# ============================================================
# OTHER KEYWORD GROUPS
# ============================================================
BUDGET_KEYWORDS = {
    "low": {"murah", "hemat", "budget", "entry"},
    "high": {"mahal", "premium", "pro"},
}

MOBILITY_KEYWORDS = {
    "high": {"ringan","travel","portable","mobile","compact"},
    "low": {"studio","tetap","statis","rig"},
}

EXPERTISE_KEYWORDS = {
    "beginner": {"pemula","beginner","baru","awal"},
    "intermediate": {"menengah","intermediate"},
    "pro": {"profesional","expert","pro","mahir"},
}

AUDIO_FLAGS = {"audio","mic","suara","podcast","voice"}
STAB_FLAGS = {"stabil","gimbal","steady","aksi","action","stabilizer"}

DAYLIGHT_TOKENS = {"siang","terang","cerah","matahari"}
LOWLIGHT_TOKENS = {"malam","gelap","lowlight","night"}


# ============================================================
# TOKENIZER
# ============================================================
def _tokenize(text: str) -> List[str]:
    raw = text.lower()
    tokens: List[str] = []
    for token in raw.replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").split():
        clean = "".join(ch for ch in token if ch.isalnum())
        if clean:
            tokens.append(clean)
    return [t for t in tokens if t not in STOPWORDS]


def _contains_any(tokens: Iterable[str], keywords: Iterable[str]) -> bool:
    return bool(set(tokens) & set(keywords))


def _canonical_hits(tokens: Iterable[str], mapping: dict) -> List[str]:
    hits = []
    for canon, variants in mapping.items():
        if _contains_any(tokens, variants):
            hits.append(canon)
    return hits


# ============================================================
# MAIN PARSER
# ============================================================
def parse_preferences(text: str) -> Preference:
    tokens = _tokenize(text)
    pref = Preference()

    # Pisahkan environment dan content type
    env_hits = _canonical_hits(tokens, {
        k: v for k, v in CANON.items() if k in {"outdoor", "indoor", "hybrid"}
    })
    focus_hits = _canonical_hits(tokens, {
        k: v for k, v in CANON.items() if k not in {"outdoor", "indoor", "hybrid"}
    })

    pref.environment.extend(env_hits)
    pref.focus.extend(focus_hits)

    # Budget
    for label, words in BUDGET_KEYWORDS.items():
        if _contains_any(tokens, words):
            pref.budget = label

    # Mobility
    for label, words in MOBILITY_KEYWORDS.items():
        if _contains_any(tokens, words):
            pref.mobility = label

    # Expertise
    for label, words in EXPERTISE_KEYWORDS.items():
        if _contains_any(tokens, words):
            pref.expertise = label

    # Audio & Stabilization flags
    pref.audio_priority = _contains_any(tokens, AUDIO_FLAGS)
    pref.stabilization_priority = _contains_any(tokens, STAB_FLAGS)

    # Lighting inference
    if _contains_any(tokens, DAYLIGHT_TOKENS):
        pref.lighting = "daylight"
    elif _contains_any(tokens, LOWLIGHT_TOKENS):
        pref.lighting = "lowlight"

    pref.environment = normalize_tags(pref.environment)
    pref.focus = normalize_tags(pref.focus)

    return pref
