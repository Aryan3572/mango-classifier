import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import json
import os

# -------------------
# Load model and classes
# -------------------
MODEL_PATH = "best_mango_model.keras"
CLASSES_PATH = "classes.json"

print("🔄 Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded successfully!")

# Load class names
with open(CLASSES_PATH, "r") as f:
    classes = json.load(f)

# -------------------
# Test image
# -------------------
# Change the image path to test a specific mango image
img_path = r"dataset\test\Sindhri\IMG_20210702_183015 - Copy.jpg"

print(f"🖼️ Testing image: {img_path}")
img = image.load_img(img_path, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

# -------------------
# Prediction
# -------------------
predictions = model.predict(img_array)
predicted_index = np.argmax(predictions)
predicted_class = classes[str(predicted_index)]
confidence = float(np.max(predictions) * 100)

print(f"🥭 Predicted mango type: {predicted_class}")
print(f"📊 Confidence: {confidence:.2f}%")
