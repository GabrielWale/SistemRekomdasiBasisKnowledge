# EQ Recommender

Sistem rekomendasi perlengkapan vlog berbasis knowledge base + NLP ringan.

## Instalasi

1. Pastikan Python 3.10+ terpasang.
2. Instal dependensi:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Unduh model spaCy multilingual kecil (opsional tetapi direkomendasikan):
   ```powershell
   python -m spacy download xx_ent_wiki_sm
   ```
   Jika model belum diunduh, parser akan otomatis menggunakan `spacy.blank("xx")` atau fallback regex sederhana.

## Cara menjalankan

- **CLI demo**
  ```powershell
  python ui/cli.py
  ```
- **GUI Tkinter**
  ```powershell
  python ui/gui.py
  ```

Masukkan deskripsi kebutuhan vlog (lingkungan, fokus, preferensi audio/stabilisasi, dsb). Parser akan mengekstrak preferensi dari teks; bila input terlalu umum, aplikasi meminta penjelasan tambahan.
