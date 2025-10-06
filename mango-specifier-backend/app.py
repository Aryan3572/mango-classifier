from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import json
import io
from PIL import Image
import os

app = Flask(__name__)

# ✅ Enable CORS for all origins (safe for testing)
# You can restrict to frontend URL later
CORS(app, origins=["https://mango-classifier-3.onrender.com"])


# Load model and classes
model = tf.keras.models.load_model("best_model.h5")
with open("classes.json", "r", encoding="utf8") as f:
    class_names = json.load(f)


def preprocess_image_bytes(b):
    img = Image.open(io.BytesIO(b)).convert("RGB").resize((224, 224))
    arr = np.array(img) / 255.0
    return np.expand_dims(arr, axis=0)


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    try:
        file_bytes = request.files["file"].read()
        x = preprocess_image_bytes(file_bytes)
        probs = model.predict(x)[0]
        idx = int(probs.argmax())
        return jsonify({
            "mangoType": class_names[idx],
            "confidence": float(probs[idx])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # ✅ Bind to Render's dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
