# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import json
import io
from PIL import Image
import os

app = Flask(__name__)

# ✅ Enable CORS only for your deployed frontend
CORS(app, origins=["https://mango-classifier-3.onrender.com"])

# Load the trained model
model = tf.keras.models.load_model("best_model.h5")

# Load class names
with open("classes.json", "r", encoding="utf8") as f:
    class_names = json.load(f)


def preprocess_image_bytes(b):
    """Preprocess uploaded image bytes for prediction."""
    img = Image.open(io.BytesIO(b)).convert("RGB").resize((224, 224))
    arr = np.array(img) / 255.0  # normalize to 0-1 if your model expects
    return np.expand_dims(arr, axis=0)


@app.route("/predict", methods=["POST"])
def predict():
    # Check if file is provided
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    try:
        # Read image bytes
        file_bytes = request.files["file"].read()

        # Preprocess and predict
        x = preprocess_image_bytes(file_bytes)
        probs = model.predict(x)[0]
        idx = int(probs.argmax())

        # Return JSON result
        return jsonify({
            "mangoType": class_names[idx],      # frontend expects 'mangoType'
            "confidence": float(probs[idx])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Use Render's assigned port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
