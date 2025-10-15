import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

app = Flask(__name__)

# -------------------
# Environment Variables
# -------------------
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN", "https://mango-classifier-3.onrender.com"
)
MODEL_PATH = os.environ.get("MODEL_PATH", "final_model.h5")
CLASSES_PATH = os.environ.get("CLASSES_PATH", "classes.json")

# -------------------
# Enable CORS
# -------------------
CORS(app, origins=FRONTEND_ORIGIN)
app.logger.info(f"✅ CORS enabled for: {FRONTEND_ORIGIN}")

# -------------------
# Load Model
# -------------------
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    app.logger.info(f"✅ Model loaded from {MODEL_PATH}")
except Exception as e:
    model = None
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
    return jsonify({"status": "ok"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    try:
        # -------------------
        # Preprocess image
        # -------------------
        image = Image.open(file.stream).convert("RGB").resize((224, 224))
        img_array = np.expand_dims(np.array(image), axis=0)
        img_array = preprocess_input(img_array)  # MobileNetV2 preprocessing

        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        # -------------------
        # Prediction
        # -------------------
        preds = model.predict(img_array, verbose=0)
        idx = int(np.argmax(preds))

        # Handle classes as list or dict
        if isinstance(classes, list):
            label = classes[idx] if idx < len(classes) else str(idx)
        else:
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
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500


# -------------------
# Main
# -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
