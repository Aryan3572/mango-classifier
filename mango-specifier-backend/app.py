# app.py
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

app = Flask(__name__)

# Frontend origin (for Render or local)
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN", "https://mango-classifier-3.onrender.com"
)

app.logger.info(f"FRONTEND_ORIGIN is set to: {FRONTEND_ORIGIN}")


# ✅ Enable CORS globally with proper configuration
CORS(app, resources={r"/*": {
    "origins": FRONTEND_ORIGIN}})

# Model and class paths
MODEL_PATH = os.environ.get("MODEL_PATH", "final_model.keras")
CLASSES_PATH = os.environ.get("CLASSES_PATH", "classes.json")

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    app.logger.info(f"✅ Loaded model from {MODEL_PATH}")
except Exception as e:
    model = None
    app.logger.error(f"❌ Model load failed: {e}")

# Load class labels
try:
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        classes = json.load(f)
except Exception:
    classes = {}
    app.logger.warning("⚠️ Classes file not found or invalid.")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "no file in request"}), 400

    file = request.files["file"]
    try:
        image = Image.open(file.stream).convert("RGB").resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        if model is None:
            return jsonify({"error": "model not loaded"}), 500

        preds = model.predict(img_array)
        idx = int(np.argmax(preds))
        label = classes.get(str(idx), str(idx))
        confidence = float(np.max(preds))

        result = {
            "mangoType": label,
            "confidence": confidence,
            "scores": preds.tolist()
        }
        return jsonify(result), 200
    except Exception as e:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "prediction failed", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
