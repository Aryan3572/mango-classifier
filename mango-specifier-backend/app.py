# app.py
import os
import json
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

app = Flask(__name__)

# Set FRONTEND_ORIGIN to your exact frontend URL or "*" for quick testing
FRONTEND_ORIGIN = os.environ.get(
    "FRONTEND_ORIGIN", "https://mango-classifier-3.onrender.com")

# Allow only the front-end origin for security (or use "*" temporarily)
CORS(app, resources={r"/predict": {
    "origins": FRONTEND_ORIGIN}}, supports_credentials=False)

MODEL_PATH = os.environ.get("MODEL_PATH", "final_model.keras")
CLASSES_PATH = os.environ.get("CLASSES_PATH", "classes.json")

# Load model & classes
model = None
classes = {}
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    app.logger.info(f"Loaded model from {MODEL_PATH}")
except Exception as e:
    app.logger.exception(f"Failed to load model: {e}")
    model = None

try:
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        classes = json.load(f)
    app.logger.info(f"Loaded classes from {CLASSES_PATH}")
except Exception:
    app.logger.warning(
        f"No classes file found at {CLASSES_PATH} or failed to read it.")
    classes = {}

# helper to ensure headers on every response


def add_cors_headers(response):
    origin = FRONTEND_ORIGIN if FRONTEND_ORIGIN != "*" else "*"
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers[
        "Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.after_request
def after_request(response):
    return add_cors_headers(response)

# health check


@app.route("/health", methods=["GET"])
def health():
    return add_cors_headers(make_response(jsonify({"status": "ok"}), 200))

# OPTIONS preflight for /predict (explicit)


@app.route("/predict", methods=["OPTIONS"])
def predict_options():
    return add_cors_headers(make_response("", 204))

# prediction endpoint


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return add_cors_headers(make_response(jsonify(
                {"error": "no file in request"}), 400))

        file = request.files["file"]
        image = Image.open(file.stream).convert("RGB").resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        if model is None:
            return add_cors_headers(make_response(jsonify(
                {"error": "model not loaded"}), 500))

        preds = model.predict(img_array)
        idx = int(np.argmax(preds))
        label = classes.get(str(idx), str(idx))
        confidence = float(np.max(preds))  # value between 0 and 1

        result = {
            "mangoType": label,       # frontend expects prediction.mangoType
            "confidence": confidence,  # frontend expects prediction.confidence
            "scores": preds.tolist()
        }
        return add_cors_headers(make_response(jsonify(result), 200))
    except Exception as e:
        app.logger.exception("Prediction failed")
        return add_cors_headers(make_response(jsonify(
            {"error": "prediction failed", "details": str(e)}), 500))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
