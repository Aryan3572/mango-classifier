import os
import json
import traceback
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from flask import Flask, request, jsonify
from flask_cors import CORS

# -------------------
# Config
# -------------------
MODEL_PATH = "best_mango_model.keras"
CLASSES_PATH = "classes.json"
UPLOAD_FOLDER = "uploads"

# -------------------
# App Init
# -------------------
app = Flask(__name__)
CORS(app, supports_credentials=True)

# -------------------
# Load Model & Classes
# -------------------
print("🔄 Loading model and classes...")
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASSES_PATH, "r") as f:
    classes = json.load(f)

print("✅ Model and classes loaded successfully!")

# -------------------
# Helper Functions
# -------------------
def preprocess_image_for_model(img_path, target_size=(224, 224)):
    """Preprocess uploaded image for model prediction."""
    img = image.load_img(img_path, target_size=target_size)
    arr = image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    try:
        arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    except Exception:
        arr = arr / 255.0
    return arr


def get_class_name(pred_index):
    """Return class name from index."""
    if isinstance(classes, list):
        return classes[pred_index] if 0 <= pred_index < len(classes) else "Unknown"
    elif isinstance(classes, dict):
        return classes.get(str(pred_index), classes.get(pred_index, "Unknown"))
    return "Unknown"


# -------------------
# Routes
# -------------------
@app.route("/", methods=["GET"])
def home():
    """Basic API test route."""
    return jsonify({"message": "✅ Mango Specifier API is running!"})


@app.route("/predict", methods=["POST"])
def upload_and_predict():
    """Handle image upload and return prediction results."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    uploaded_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(uploaded_path)

    try:
        # Step 1: Preprocess and predict
        img_arr = preprocess_image_for_model(uploaded_path)
        preds = model.predict(img_arr)[0]  # flatten to 1D array

        # Step 2: Top-3 predictions
        top_indices = preds.argsort()[-3:][::-1]
        top_predictions = [
            {
                "label": get_class_name(int(i)),
                "confidence": round(float(preds[i] * 100.0), 2)
            }
            for i in top_indices
        ]

        # Step 3: Best prediction
        predicted_class = top_predictions[0]["label"]
        confidence = top_predictions[0]["confidence"]

        # Step 4: Return final response (no GradCAM)
        response = {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top_predictions": top_predictions
        }
        return jsonify(response)

    except Exception as e:
        print("❌ Prediction failed:", e)
        traceback.print_exc()
        return jsonify({
            "predicted_class": "Unknown",
            "confidence": 0.0,
            "top_predictions": [],
            "error": str(e)
        }), 500

    finally:
        # Cleanup uploaded files
        try:
            if os.path.exists(uploaded_path):
                os.remove(uploaded_path)
        except Exception:
            pass


# -------------------
# 📊 Model Performance Dashboard
# -------------------
@app.route("/metrics", methods=["GET"])
def get_model_metrics():
    """Return model performance metrics (mock or real values)."""
    metrics = {
        "accuracy": 94.87,
        "precision": 93.45,
        "recall": 92.60,
        "f1_score": 93.02,
        "last_updated": "2025-10-28"
    }
    return jsonify(metrics)


# -------------------
# Run
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
