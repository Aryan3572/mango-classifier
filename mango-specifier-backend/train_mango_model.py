import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# ------------------------
# Paths and basic settings
# ------------------------
BASE_DIR = "dataset"
TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "val")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
LR = 0.0001

# ------------------------
# Data Generators
# ------------------------
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=25,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode="nearest",
)

val_datagen = ImageDataGenerator(rescale=1.0 / 255)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
)

# ------------------------
# Model Definition
# ------------------------
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze feature extractor

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.4),
    Dense(128, activation="relu"),
    Dropout(0.3),
    Dense(train_generator.num_classes, activation="softmax"),
])

model.compile(
    optimizer=Adam(learning_rate=LR),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# ------------------------
# Training Callbacks
# ------------------------
checkpoint = ModelCheckpoint(
    "best_mango_model.keras",
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1,
)

early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

# ------------------------
# Train the Model
# ------------------------
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    callbacks=[checkpoint, early_stop],
)

# ------------------------
# Save Final Model
# ------------------------
model.save("final_mango_model.keras")
print("✅ Model training complete and saved as final_mango_model.keras")


# -------------------------------
# Save class names to classes.json
# -------------------------------
import json

# Get class names from your training data
class_names = train_generator.class_indices
# Invert the dictionary to map index → class name
classes = {v: k for k, v in class_names.items()}

# Save to a JSON file
with open("classes.json", "w") as f:
    json.dump(classes, f, indent=4)

print("✅ Classes saved to classes.json")

