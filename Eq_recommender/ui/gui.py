"""Tkinter front-end for the EQ recommender."""
from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, messagebox

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from recommender.engine import recommend_from_text


class RecommenderApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.master.title("EQ Recommender")
        self.master.geometry("720x480")
        self._build_widgets()

    def _build_widgets(self) -> None:
        ttk.Label(self, text="Deskripsikan kebutuhan vlog Anda:").grid(row=0, column=0, sticky="w")

        self.input_text = tk.Text(self, height=4, width=70)
        self.input_text.grid(row=1, column=0, columnspan=2, pady=(4, 8), sticky="nsew")

        action_frame = ttk.Frame(self)
        action_frame.grid(row=2, column=0, columnspan=2, sticky="e")
        ttk.Button(action_frame, text="Rekomendasikan", command=self._run_recommendation).pack(side=tk.RIGHT)

        ttk.Separator(self, orient="horizontal").grid(row=3, column=0, columnspan=2, pady=8, sticky="ew")

        self.results = tk.Text(self, state="disabled", width=70, height=15)
        self.results.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.grid(row=0, column=0, sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)

    def _run_recommendation(self) -> None:
        user_text = self.input_text.get("1.0", tk.END).strip()
        if not user_text:
            messagebox.showwarning("Input kosong", "Silakan isi kebutuhan vlog terlebih dahulu.")
            return
        try:
            results = recommend_from_text(user_text, top_k=3)
        except ValueError as exc:
            messagebox.showwarning("Input kurang jelas", str(exc))
            return
        except Exception as exc:  # pragma: no cover - Tkinter only
            messagebox.showerror("Terjadi kesalahan", str(exc))
            return
        self._render_results(results)

    def _render_results(self, results: list[dict]) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", tk.END)
        if not results:
            self.results.insert(tk.END, "Tidak ditemukan rekomendasi yang cocok.\n")
        for idx, item in enumerate(results, start=1):
            kit = item["kit"]
            self.results.insert(
                tk.END,
                (
                    f"{idx}. {kit.name} (skor {item['score']:.2f})\n"
                    f"   Fokus : {', '.join(kit.best_for) or '-'}\n"
                    f"   Lingkungan : {', '.join(kit.environment)}\n"
                    f"   Komponen : {', '.join(kit.components)}\n\n"
                ),
            )
        self.results.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    RecommenderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
