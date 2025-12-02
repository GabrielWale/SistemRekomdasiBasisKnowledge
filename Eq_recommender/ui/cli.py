"""Minimal CLI driver to try the recommendation pipeline."""
from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from recommender.engine import recommend_from_text


def main() -> None:
    print("=== EQ Recommender Demo ===")
    query = input("Tuliskan kebutuhan vlog Anda: ")
    try:
        results = recommend_from_text(query, top_k=3)
    except ValueError as exc:
        print(f"Input kurang jelas: {exc}")
        return
    print("\nRekomendasi teratas:")
    for idx, item in enumerate(results, start=1):
        kit = item["kit"]
        print(f"{idx}. {kit.name} (skor {item['score']:.2f})")
        print(f"   Fokus: {', '.join(kit.best_for) or '-'} | Lingkungan: {', '.join(kit.environment)}")
        print(f"   Komponen: {', '.join(kit.components)}")
        print()


if __name__ == "__main__":
    main()
