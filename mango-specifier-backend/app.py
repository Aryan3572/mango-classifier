import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # disable GPU on Render
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"   # suppress TensorFlow warnings


app = Flask(__name__)

# -------------------
# Environment Variables
# -------------------
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN", "https://mango-classifier-3.onrender.com")
MODEL_PATH = os.environ.get("MODEL_PATH", "final_model.keras")
CLASSES_PATH = os.environ.get("CLASSES_PATH", "classes.json")

# -------------------
# Enable CORS
# -------------------
CORS(app, origins=FRONTEND_ORIGIN)
app.logger.info(f"✅ CORS enabled for: {FRONTEND_ORIGIN}")

# -------------------
# Load Model (with fallback)
# -------------------
model = None
try:
    if not os.path.exists(MODEL_PATH):
        alt_path = MODEL_PATH.replace(".keras", ".h5")
        if os.path.exists(alt_path):
            MODEL_PATH = alt_path
            app.logger.warning(f"⚠️ Using fallback model file: {MODEL_PATH}")
        else:
            raise FileNotFoundError(
                f"No model file found at {MODEL_PATH} or {alt_path}")

    model = tf.keras.models.load_model(MODEL_PATH)
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

    file = request.files["file"]
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # -------------------
        # Preprocess image
        # -------------------
        image = Image.open(file.stream).convert("RGB").resize((224, 224))
        img_array = np.expand_dims(np.array(image), axis=0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input
        (img_array)

        # -------------------
        # Prediction
        # -------------------
        preds = model.predict(img_array, verbose=0)
        idx = int(np.argmax(preds))
        confidence = float(np.max(preds))

        # Handle both list and dict formats for classes
        label = (
            classes[idx]
            if isinstance(classes, list) and idx < len(classes)
            else classes.get(str(idx), f"Class {idx}")
            if isinstance(classes, dict)
            else f"Class {idx}"
        )

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
