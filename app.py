# app.py
from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import json
import io
from PIL import Image

app = Flask(__name__)
model = tf.keras.models.load_model("best_model.h5")
with open("classes.json", "r", encoding="utf8") as f:
    class_names = json.load(f)


def preprocess_image_bytes(b):
    img = Image.open(io.BytesIO(b)).convert("RGB").resize((224, 224))
    arr = np.array(img)/255.0
    return np.expand_dims(arr, axis=0)


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "no file provided"}), 400
    f = request.files["file"].read()
    x = preprocess_image_bytes(f)
    probs = model.predict(x)[0]
    idx = int(probs.argmax())
    return jsonify({
        "label": class_names[idx],
        "confidence": float(probs[idx])
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
