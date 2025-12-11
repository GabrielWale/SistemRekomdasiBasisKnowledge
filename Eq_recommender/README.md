## Struktur & Fungsi Utama (Eq_recommender)

### Backend (app.py — Flask)
- **Model DB**: `kategori_alat`, `alat`, `user_input`, `rekomendasi`
- **CRUD API**:
  - `/api/categories`
  - `/api/alats` (GET/POST/PUT/DELETE)
- **Rekomendasi API**:
  - `/api/recommend` (POST) → menyimpan `user_input` dan hasil ke tabel rekomendasi
- **NLP + Scoring**:
  - Tokenisasi + stopword + sinonim (outdoor/siang/cerah/travel/vlog/podcast/action/lowlight)
  - TF-IDF n-gram (1,2) + overlap
  - Penalti jika query outdoor/siang tapi alat low-light
  - Faktor budget dan rating
  - Simpan alasan (sim/overlap/budget/penalty)
- **Seed data**: kamera, mic, lampu, gimbal
- **CLI**: `flask --app app.py initdb`

### Frontend
- **static/index.html** → SPA sederhana dengan 2 tab: CRUD alat & form rekomendasi
- **static/styles.css** → Tema gelap modern, grid cards, form styling
- **app.js** → Logika tab, fetch CRUD, kirim request rekomendasi, render hasil (skor/sim/overlap)

### NLP / Rule yang diterapkan
- **Sinonim kanonikal**:
  - *outdoor*: luar, siang, cerah, matahari, travel, jalan, alam
  - *indoor/studio*
  - *travel/vlog*
  - *podcast/interview*
  - *action*
  - *lowlight*: gelap, malam, lowlight
- **Stopword**: bahasa sehari-hari + filler
- **Scoring formula**:  
  

\[
  0.6 \cdot sim + 0.25 \cdot overlap + 0.05 \cdot rating + 0.1 \cdot budget\_factor - penalty\_lowlight
  \]

  
  Penalti 0.15 bila query outdoor/siang tapi alat ter-tag lowlight

### Data
- **Database**: `app.db` (SQLite) otomatis dibuat; sudah di-.gitignore
- **Seed alat contoh**: Sony ZV-1, Canon R6, Rode Wireless GO II, Godox SL60W, DJI RS3 Mini
- **equipment_data.csv**: masih untuk engine lama; belum dipakai oleh Flask app baru
