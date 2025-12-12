# Eq_recommender/import_equipment.py
import csv
from pathlib import Path

# import app & db + models langsung dari app.py
from app import app, db, Category, Alat

CSV_PATH = Path(__file__).parent / "data" / "equipment_data2.csv"

def get_or_create_category(name: str):
    name = (name or "Umum").strip()
    cat = Category.query.filter_by(nama_kategori=name).first()
    if not cat:
        cat = Category(nama_kategori=name)
        db.session.add(cat)
        db.session.commit()
    return cat

def import_data():
    if not CSV_PATH.exists():
        print("CSV file not found:", CSV_PATH)
        return

    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        added = 0
        skipped = 0

        for row in reader:
            nama = (row.get("nama_alat") or "").strip()
            if not nama:
                print("SKIP row tanpa nama_alat")
                skipped += 1
                continue

            # category column in CSV may be "kategori"
            kategori_name = row.get("kategori") or row.get("category") or "Umum"
            kategori_obj = get_or_create_category(kategori_name.strip())

            # cek duplikat berdasarkan nama alat (case-insensitive)
            exist = Alat.query.filter(db.func.lower(Alat.nama_alat) == nama.lower()).first()
            if exist:
                print(f"SKIP (sudah ada): {nama}")
                skipped += 1
                continue

            # safe parse numeric fields
            try:
                harga = int(float(row.get("harga_sewa") or 0))
            except Exception:
                harga = 0
            try:
                stok = int(float(row.get("stok") or 0))
            except Exception:
                stok = 0
            try:
                rating = float(row.get("rating_alat") or 0.0)
            except Exception:
                rating = 0.0

            alat = Alat(
                id_kategori=kategori_obj.id_kategori,
                nama_alat=nama,
                deskripsi=row.get("deskripsi", "").strip(),
                kebutuhan_konten=row.get("kebutuhan_konten", "").strip(),
                harga_sewa=harga,
                stok=stok,
                rating_alat=rating,
                gambar=row.get("gambar", "").strip() or None,
            )
            db.session.add(alat)
            added += 1

        try:
            db.session.commit()
        except Exception as e:
            print("ERROR saat commit:", e)
            db.session.rollback()
            return

        print(f"IMPORT SELESAI — Added={added}, Skipped={skipped}")

if __name__ == "__main__":
    # run inside flask app context so SQLAlchemy works
    with app.app_context():
        import_data()
