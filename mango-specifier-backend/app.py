import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# -------------------
# Disable GPU & reduce TF logs (Render/Heroku is CPU-only)
# -------------------
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

app = Flask(__name__)

# -------------------
# Environment Variables
# -------------------
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN", "https://mango-classifier.vercel.app"
)
MODEL_PATH = os.environ.get("MODEL_PATH", "final_model.keras")
CLASSES_PATH = os.environ.get("CLASSES_PATH", "classes.json")

# -------------------
# Enable CORS
# -------------------
CORS(app, origins=[FRONTEND_ORIGIN])
app.logger.info(f"✅ CORS enabled for: {FRONTEND_ORIGIN}")

# -------------------
# Load Model
# -------------------
model = None
try:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    app.logger.info(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    app.logger.error(f"❌ Failed to load model: {e}")

# -------------------
# Load Classes
# -------------------
try:
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        classes = json.load(f)
    app.logger.info(f"✅ Classes loaded from {CLASSES_PATH}")
except Exception as e:
    classes = []
    app.logger.warning(f"⚠️ Failed to load classes: {e}")


# -------------------
# Routes
# -------------------
@app.route("/health", methods=["GET"])
def health():
    """Health check route."""
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    """Predict the mango variety."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        file = request.files["file"]

        # -------------------
        # Preprocess image
        # -------------------
        image = Image.open(file.stream).convert("RGB").resize((224, 224))
        img_array = np.expand_dims(np.array(image), axis=0)
        img_array = preprocess_input(img_array)

        # -------------------
        # Prediction
        # -------------------
        preds = model.predict(img_array, verbose=0)
        idx = int(np.argmax(preds))
        confidence = float(np.max(preds))

        # Handle classes (list or dict)
        if isinstance(classes, list):
            label = classes[idx] if idx < len(classes) else f"Class {idx}"
        else:
            label = classes.get(str(idx), f"Class {idx}")

        result = {
            "mangoType": label,
            "confidence": confidence,
            "scores": preds.tolist()
        }

        return jsonify(result), 200

    except Exception as e:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500


# -------------------
# Main
# -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
