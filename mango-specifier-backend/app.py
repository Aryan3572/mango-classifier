# app.py
import os
import re
import json
import sqlite3
import traceback
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
from collections import Counter


# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
MODEL_PATH = "best_mango_model.keras"
CLASSES_PATH = "classes.json"
METADATA_PATH = "mango_metadata.json"
UPLOAD_FOLDER = "uploads"
DB_PATH = "mango_users.db"
SECRET_KEY = os.environ.get("MANGO_SECRET_KEY", "super_secret_key_123")
JWT_EXPIRES_DAYS = 10

app = Flask(__name__)
# global CORS - allow local frontend during development
CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
app.config["JSON_AS_ASCII"] = False

# ---------------------------------------------------
# DATABASE HELPERS
# ---------------------------------------------------


def get_db():
    if "_db" not in g:
        g._db = sqlite3.connect(DB_PATH)
        g._db.row_factory = sqlite3.Row
    return g._db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("_db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TEXT
        );
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_name TEXT,
            predicted_class TEXT,
            normalized_class TEXT,
            confidence REAL,
            metadata_snapshot TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()


# ---------------------------------------------------
# LOAD MODEL + METADATA
# ---------------------------------------------------
print("🔄 Loading model and metadata...")

# load model (if file missing this will raise — ensure file exists)
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    classes = json.load(f)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

print("✅ Model + Metadata Loaded")


# ---------------------------------------------------
# NORMALIZATION (robust)
# ---------------------------------------------------
# small manual alias map for tricky names (expand as needed)
ALIAS_MAP = {
    "anwar ratol": "anwar_ratol",
    "anwar ratool": "anwar_ratol",
    "anwar_ratool": "anwar_ratol",
    "dussehri": "dasheri",
    "dosehri": "dasheri",
    "dosehri ": "dasheri",
    "dashehari": "dasheri",
    "alphonso (hapus)": "alphonso",
    "alphonso hapus": "alphonso",
}

_slug_re = re.compile(r"[^a-z0-9]+")


def normalize_label_to_key(label: str) -> str:
    """
    Convert arbitrary model label into metadata key:
    - check alias map (case-insensitive)
    - fallback: lowercase + replace non-alnum with underscores
    """
    if not label:
        return label
    lbl = label.strip()
    low = lbl.lower()
    if low in ALIAS_MAP:
        return ALIAS_MAP[low]
    # if label is already a slug-like key in metadata, keep it
    candidate = _slug_re.sub("_", low).strip("_")
    return candidate


def get_variety_key_from_slug(slug: str) -> str:
    """
    Given a path slug from URL, tolerate spaces, dashes, underscores, case
    and return a metadata key if exists, else None.
    """
    if not slug:
        return None
    s = slug.strip().lower()
    # try direct matches
    if s in metadata:
        return s
    # replace spaces/dashes with underscores
    s2 = _slug_re.sub("_", s).strip("_")
    if s2 in metadata:
        return s2
    # try alias map
    if s in ALIAS_MAP:
        return ALIAS_MAP[s]
    if s2 in ALIAS_MAP:
        return ALIAS_MAP[s2]
    return None


# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    arr = image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    try:
        arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    except Exception:
        arr = arr / 255.0
    return arr


def get_class_name(i):
    """Return a readable label from classes.json whether list or dict."""
    try:
        if isinstance(classes, list):
            return classes[int(i)]
        if isinstance(classes, dict):
            # classes might be like {"0":"alphonso", "1":"chaunsa"}
            return classes.get(str(i), classes.get(i, str(i)))
    except Exception:
        return str(i)
    return str(i)


def json_response_ok(data, status=200):
    return jsonify(data), status


# token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get("Authorization", "") or request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            token = auth.replace("Bearer ", "", 1).strip()
        elif auth:
            token = auth.strip()

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # attach user info to request context for use in routes
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------
@app.route("/auth/signup", methods=["POST", "OPTIONS"])
def signup():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    raw_password = data.get("password", "")

    if not email or not raw_password:
        return jsonify({"error": "Email & password required"}), 400

    password = generate_password_hash(raw_password)
    created_at = datetime.utcnow().isoformat()

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?,?,?,?)",
            (name, email, password, created_at),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Account created"}), 201


@app.route("/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email & password required"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "id": user["id"],
            "email": user["email"],
            "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRES_DAYS),
            "iat": datetime.utcnow(),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    # ensure token is string (pyjwt returns str in pyjwt>=2)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return jsonify({"token": token})


# ---------------------------------------------------
# MANGO ROUTES
# ---------------------------------------------------
@app.route("/metrics", methods=["GET"])
def metrics():
    return jsonify(
        {
            "accuracy": 94.87,
            "precision": 93.45,
            "recall": 92.60,
            "f1_score": 93.02,
        }
    )


@app.route("/varieties", methods=["GET"])
def all_varieties():
    return jsonify(list(metadata.keys()))


@app.route("/variety/<slug>", methods=["GET"])
def get_variety(slug):
    # tolerant lookup
    key = get_variety_key_from_slug(slug)
    if key:
        return jsonify(metadata[key])
    return jsonify({"error": "Unknown variety"}), 404


@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():
    # allow preflight
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = file.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        arr = preprocess_image(path)
        preds = model.predict(arr)[0]

        top = preds.argsort()[-3:][::-1]
        top_preds = []
        for i in top:
            label = get_class_name(int(i))
            conf = round(float(preds[i] * 100.0), 2)
            top_preds.append({"label": label, "confidence": conf})

        best_label = top_preds[0]["label"]
        normalized_key = normalize_label_to_key(best_label)

        return jsonify(
    {
        "predicted_class": best_label,
        "normalized_class": normalized_key,
        "confidence": top_preds[0]["confidence"],
        "top_predictions": top_preds,

        # -------- Dataset specifications (Feature-1 for website) --------
        "dataset_info": {
            "camera_model": "12MP smartphone camera",
            "capture_settings": "Auto exposure, natural lighting, handheld capture",
            "capture_environments": "Daylight, shaded areas and indoor ambient lighting",
            "background_standardization": "Natural background without strict background standardization",
            "capture_angles": "Front, side and slightly top-angled views",
            "collection_location": "Pune, Maharashtra, India",
            "season": "April–June (mango harvesting season)",
            "collection_stage": "Market stage",
            "labeling_protocol": "Images were manually labeled by the authors and verified through visual inspection",
            "total_varieties": len(metadata)
        }
    }
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


# ---------------------------------------------------
# Save prediction (authenticated)
# ---------------------------------------------------
@app.route("/predictions", methods=["OPTIONS", "POST"])
@token_required
def save_prediction():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json() or {}
    predicted_class = data.get("predicted_class")
    normalized_class = data.get("normalized_class") or normalize_label_to_key(predicted_class)
    confidence = data.get("confidence")
    image_name = data.get("image_name", None)
    metadata_snapshot = data.get("metadata")  # store a snapshot (dict) as JSON

    user_id = request.user.get("id")

    if not user_id:
        return jsonify({"error": "Invalid user"}), 401

    created_at = datetime.utcnow().isoformat()

    db = get_db()
    try:
        db.execute(
            "INSERT INTO predictions (user_id, image_name, predicted_class, normalized_class, confidence, metadata_snapshot, created_at) VALUES (?,?,?,?,?,?,?)",
            (
                user_id,
                image_name,
                predicted_class,
                normalized_class,
                confidence,
                json.dumps(metadata_snapshot, ensure_ascii=False),
                created_at,
            ),
        )
        db.commit()
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Prediction saved"}), 201

# ---------------------------------------------------
# Dataset Specifications
# ---------------------------------------------------


@app.route("/dataset-info", methods=["GET"])
def dataset_info():
    data = {
        "camera_model": "12MP smartphone camera",
        "capture_settings": "Auto exposure, natural lighting, handheld capture",
        "capture_environments": "Daylight, shaded areas and indoor ambient lighting",
        "background_standardization": "Natural background without strict background standardization",
        "capture_angles": "Front, side and slightly top-angled views",
        "collection_location": "Pune, Maharashtra, India",   # <-- change if needed
        "season": "April–June (mango harvesting season)",
        "collection_stage": "Market stage",
        "labeling_protocol": "Images were manually labeled by the authors and verified through visual inspection",
        "total_varieties": len(metadata),
        "images_per_variety": {
            k: len(v.get("samples", [])) if isinstance(v, dict) else None
            for k, v in metadata.items()
        }
    }

    return jsonify(data)

# ---------------------------------------------------
# Statistical analysis – Class distribution
# ---------------------------------------------------

@app.route("/stats/class-distribution", methods=["GET"])
def class_distribution():
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")

    if not os.path.exists(dataset_dir):
        return jsonify({"error": "dataset folder not found"}), 404

    counts = {}

    for cls in sorted(os.listdir(dataset_dir)):
        cls_path = os.path.join(dataset_dir, cls)
        if os.path.isdir(cls_path):
            counts[cls] = len([
                f for f in os.listdir(cls_path)
                if os.path.isfile(os.path.join(cls_path, f))
            ])

    if not counts:
        return jsonify({"error": "no class folders found"}), 400

    values = list(counts.values())
    max_count = max(values)
    min_count = min(values)

    imbalance_ratio = round(max_count / min_count, 3) if min_count > 0 else None

    return jsonify({
        "total_classes": len(counts),
        "total_images": sum(values),
        "images_per_class": counts,
        "max_class_size": max_count,
        "min_class_size": min_count,
        "imbalance_ratio": imbalance_ratio
    })


# ---------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------
if __name__ == "__main__":
    # ensure DB and tables are present inside app context
    with app.app_context():
        init_db()
    # run
    app.run(debug=True)
