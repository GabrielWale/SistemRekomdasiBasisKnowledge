import os
from datetime import datetime
from typing import List

from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
except ImportError:
    StemmerFactory = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Category(db.Model):
    __tablename__ = "kategori_alat"
    id_kategori = db.Column(db.Integer, primary_key=True)
    nama_kategori = db.Column(db.String(100), nullable=False, unique=True)
    alat = db.relationship("Alat", backref="kategori", lazy=True)


class Alat(db.Model):
    __tablename__ = "alat"
    id_alat = db.Column(db.Integer, primary_key=True)
    id_kategori = db.Column(db.Integer, db.ForeignKey("kategori_alat.id_kategori"), nullable=False)
    nama_alat = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    kebutuhan_konten = db.Column(db.Text, nullable=True)
    harga_sewa = db.Column(db.Integer, nullable=False, default=0)
    stok = db.Column(db.Integer, nullable=False, default=0)
    rating_alat = db.Column(db.Float, nullable=False, default=0.0)
    gambar = db.Column(db.String(255), nullable=True)


class UserInput(db.Model):
    __tablename__ = "user_input"
    id_input = db.Column(db.Integer, primary_key=True)
    jenis_konten = db.Column(db.String(200), nullable=False)
    deskripsi_konten = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Integer, nullable=False, default=0)
    lokasi = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Rekomendasi(db.Model):
    __tablename__ = "rekomendasi"
    id_rekom = db.Column(db.Integer, primary_key=True)
    id_input = db.Column(db.Integer, db.ForeignKey("user_input.id_input"), nullable=False)
    id_alat = db.Column(db.Integer, db.ForeignKey("alat.id_alat"), nullable=False)
    skor_kecocokan = db.Column(db.Float, nullable=False, default=0.0)
    alasan = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    alat = db.relationship("Alat")
    user_input = db.relationship("UserInput")


STOPWORDS = {
    "dan", "yang", "untuk", "dengan", "di", "ke", "dari", "atau", "pada", "ini",
    "itu", "saat", "karena", "dalam", "agar", "bagi", "guna", "serta", "ada", "akan",
    "tidak", "ya", "kok", "lah", "kah", "nih", "deh", "dong", "banget", "aja", "juga",
    "misalnya", "contoh", "seperti", "jadi", "kalau", "bila", "sudah", "belum",
    "saya", "aku", "kamu", "ingin", "pengen", "membuat", "buat", "konten", "kontennya", "kontenmu",
    "hari", "waktu",
}

CANON = {
    "travel": {"travel", "jalan", "jalan2", "trip", "liburan", "backpacker"},
    "outdoor": {"outdoor", "luar", "ruangan", "alam", "nature", "hiking", "camping", "siang", "terang", "matahari", "cerah"},
    "indoor": {"indoor", "studio", "ruangan", "setup"},
    "action": {"action", "sport", "olahraga", "trail"},
    "wedding": {"wedding", "nikah", "married", "pengantin"},
    "podcast": {"podcast", "talkshow", "interview", "talking", "head"},
    "interview": {"interview", "wawancara"},
    "studio": {"studio", "indoor"},
    "vlog": {"vlog", "konten", "harian", "daily"},
    "lowlight": {"low", "light", "lowlight", "gelap", "malam"},
}

NEGATIVE_CUES = {
    "lowlight": {"low", "light", "lowlight", "gelap", "malam"},
}

stemmer = StemmerFactory().create_stemmer() if StemmerFactory else None


def normalize_tokens(tokens: List[str]) -> List[str]:
    normalized: List[str] = []
    for tok in tokens:
        placed = False
        for canon, variants in CANON.items():
            if tok in variants:
                normalized.append(canon)
                placed = True
                break
        if not placed:
            normalized.append(tok)
    return normalized


def preprocess_tokens(text: str) -> List[str]:
    if not text:
        return []
    raw = text.lower()
    tokens: List[str] = []
    for token in raw.replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").split():
        clean = "".join(ch for ch in token if ch.isalnum())
        if clean:
            tokens.append(clean)
    tokens = [t for t in tokens if t not in STOPWORDS]
    tokens = normalize_tokens(tokens)
    if stemmer:
        tokens = [stemmer.stem(t) for t in tokens]
    return [t for t in tokens if t]


def detect_flags(tokens: List[str]):
    token_set = set(tokens)
    is_lowlight = bool(token_set & NEGATIVE_CUES["lowlight"])
    is_outdoor = "outdoor" in token_set or "travel" in token_set
    is_indoor = "indoor" in token_set or "studio" in token_set
    return {
        "lowlight": is_lowlight,
        "outdoor": is_outdoor,
        "indoor": is_indoor,
    }


def simple_preprocess(text: str) -> str:
    return " ".join(preprocess_tokens(text))


def seed_data():
    if Category.query.count() == 0:
        for name in ["Kamera", "Audio", "Pencahayaan", "Stabilisasi"]:
            db.session.add(Category(nama_kategori=name))
        db.session.commit()

    if Alat.query.count() == 0:
        cam = Category.query.filter_by(nama_kategori="Kamera").first()
        mic = Category.query.filter_by(nama_kategori="Audio").first()
        light = Category.query.filter_by(nama_kategori="Pencahayaan").first()
        stab = Category.query.filter_by(nama_kategori="Stabilisasi").first()

        samples = [
            Alat(id_kategori=cam.id_kategori, nama_alat="Sony ZV-1", deskripsi="Kamera compact untuk vlog",
                 kebutuhan_konten="vlog travel daily low light", harga_sewa=250, stok=5, rating_alat=4.5),
            Alat(id_kategori=cam.id_kategori, nama_alat="Canon EOS R6", deskripsi="Mirrorless full-frame",
                 kebutuhan_konten="wedding cinematic low light", harga_sewa=700, stok=3, rating_alat=4.7),
            Alat(id_kategori=mic.id_kategori, nama_alat="Rode Wireless GO II", deskripsi="Mic wireless interview",
                 kebutuhan_konten="interview podcast vlog", harga_sewa=120, stok=10, rating_alat=4.6),
            Alat(id_kategori=light.id_kategori, nama_alat="Godox SL60W", deskripsi="Lampu continuous",
                 kebutuhan_konten="studio podcast indoor", harga_sewa=80, stok=7, rating_alat=4.4),
            Alat(id_kategori=stab.id_kategori, nama_alat="DJI RS3 Mini", deskripsi="Gimbal ringan",
                 kebutuhan_konten="cinematic travel action", harga_sewa=150, stok=4, rating_alat=4.5),
        ]
        db.session.add_all(samples)
        db.session.commit()


def alat_to_dict(item: Alat):
    return {
        "id_alat": item.id_alat,
        "id_kategori": item.id_kategori,
        "nama_alat": item.nama_alat,
        "deskripsi": item.deskripsi,
        "kebutuhan_konten": item.kebutuhan_konten,
        "harga_sewa": item.harga_sewa,
        "stok": item.stok,
        "rating_alat": item.rating_alat,
        "gambar": item.gambar,
        "kategori": item.kategori.nama_kategori if item.kategori else None,
    }


@app.route("/api/categories", methods=["GET"])
def list_categories():
    data = Category.query.order_by(Category.nama_kategori).all()
    return jsonify([{"id_kategori": c.id_kategori, "nama_kategori": c.nama_kategori} for c in data])


@app.route("/api/alats", methods=["GET", "POST"])
def alats():
    if request.method == "GET":
        items = Alat.query.order_by(Alat.id_alat.desc()).all()
        return jsonify([alat_to_dict(i) for i in items])

    payload = request.json or {}
    item = Alat(
        id_kategori=payload.get("id_kategori"),
        nama_alat=payload.get("nama_alat"),
        deskripsi=payload.get("deskripsi"),
        kebutuhan_konten=payload.get("kebutuhan_konten"),
        harga_sewa=payload.get("harga_sewa", 0),
        stok=payload.get("stok", 0),
        rating_alat=payload.get("rating_alat", 0.0),
        gambar=payload.get("gambar"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(alat_to_dict(item)), 201


@app.route("/api/alats/<int:alat_id>", methods=["PUT", "DELETE"])
def alats_detail(alat_id):
    item = Alat.query.get_or_404(alat_id)
    if request.method == "DELETE":
        db.session.delete(item)
        db.session.commit()
        return "", 204

    payload = request.json or {}
    for field in ["id_kategori", "nama_alat", "deskripsi", "kebutuhan_konten", "harga_sewa", "stok", "rating_alat", "gambar"]:
        if field in payload:
            setattr(item, field, payload[field])
    db.session.commit()
    return jsonify(alat_to_dict(item))


@app.route("/api/recommend", methods=["POST"])
def recommend():
    payload = request.json or {}
    jenis_konten = payload.get("jenis_konten", "")
    deskripsi_konten = payload.get("deskripsi_konten", "")
    budget = int(payload.get("budget", 0))
    lokasi = payload.get("lokasi", "")

    user_text = f"{jenis_konten} {deskripsi_konten}"
    user_input = UserInput(
        jenis_konten=jenis_konten,
        deskripsi_konten=deskripsi_konten,
        budget=budget,
        lokasi=lokasi,
    )
    db.session.add(user_input)
    db.session.commit()

    alat_list: List[Alat] = Alat.query.all()
    if not alat_list:
        return jsonify({"message": "No alat available"}), 400

    alat_tokens_list = [preprocess_tokens(f"{a.kebutuhan_konten} {a.deskripsi}") for a in alat_list]
    user_tokens = preprocess_tokens(user_text)
    user_flags = detect_flags(user_tokens)

    corpus = [" ".join(tokens) for tokens in alat_tokens_list]
    corpus.append(" ".join(user_tokens))

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf = vectorizer.fit_transform(corpus)
    user_vec = tfidf[-1]
    alat_vecs = tfidf[:-1]

    sims = linear_kernel(user_vec, alat_vecs).flatten()
    user_set = set(user_tokens)

    results = []
    for idx, (alat, sim) in enumerate(zip(alat_list, sims)):
        alat_tokens = alat_tokens_list[idx]
        alat_set = set(alat_tokens)
        overlap = 0.0 if not user_set else len(user_set & alat_set) / len(user_set)

        if overlap <= 0 and sim < 0.02:
            continue

        alat_flags = detect_flags(alat_tokens)

        penalty = 0.0
        if user_flags.get("outdoor") and not user_flags.get("lowlight") and alat_flags.get("lowlight"):
            penalty = 0.15

        budget_factor = 1.0 if budget <= 0 else max(0.25, min(1.0, (budget - alat.harga_sewa) / max(budget, 1)))
        score = float(sim * 0.6 + overlap * 0.25 + alat.rating_alat * 0.05 + budget_factor * 0.1 - penalty)

        if budget <= 0 or alat.harga_sewa <= budget * 1.2:
            results.append((alat, score, sim, budget_factor, overlap, penalty, alat_flags))

    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:10]

    for alat, score, sim, budget_factor, overlap, penalty, alat_flags in top_results:
        alasan = (
            f"similarity={sim:.2f}, overlap={overlap:.2f}, rating={alat.rating_alat}, "
            f"budget_factor={budget_factor:.2f}, penalty={penalty:.2f}, flags={alat_flags}"
        )
        rec = Rekomendasi(
            id_input=user_input.id_input,
            id_alat=alat.id_alat,
            skor_kecocokan=score,
            alasan=alasan,
        )
        db.session.add(rec)
    db.session.commit()

    response = [
        {
            "alat": alat_to_dict(alat),
            "skor": score,
            "sim": sim,
            "budget_factor": budget_factor,
            "overlap": overlap,
            "penalty": penalty,
            "alat_flags": alat_flags,
        }
        for alat, score, sim, budget_factor, overlap, penalty, alat_flags in top_results
    ]
    return jsonify(response)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.cli.command("initdb")
def initdb():
    db.drop_all()
    db.create_all()
    seed_data()
    print("Database initialized with seed data")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
