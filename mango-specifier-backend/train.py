import os
import keras
from keras import layers
from keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
import tensorflow as tf
import json

# ------------------- Disable GPU -------------------
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ------------------- Paths and Settings -------------------
DATA_DIR = "dataset"  # dataset/train and dataset/val
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 25
AUTOTUNE = tf.data.AUTOTUNE

# ------------------- Load datasets -------------------
train_ds = keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "train"),
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    seed=123
)
val_ds = keras.utils.image_dataset_from_directory(
    os.path.join(DATA_DIR, "val"),
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    seed=123
)

# ------------------- Classes -------------------
class_names = train_ds.class_names
print("✅ Classes found:", class_names)

with open("classes.json", "w", encoding="utf8") as f:
    json.dump(class_names, f, ensure_ascii=False, indent=2)

train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# ------------------- Data Augmentation -------------------
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
], name="data_augmentation")

# ------------------- Base Model -------------------
base_model = MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = True
for layer in base_model.layers[:100]:
    layer.trainable = False

# ------------------- Build Model -------------------
inputs = keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
x = preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(class_names), activation="softmax")(x)

model = keras.Model(inputs, outputs, name="mango_classifier")

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# ------------------- Callbacks -------------------
callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath="final_model.keras",
        save_best_only=True,
        monitor="val_accuracy",
        mode="max",
        verbose=1
    ),
    keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=5,
        restore_best_weights=True
    )
]

# ------------------- Train -------------------
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks
)

model.save("final_model.keras")
print("✅ Training complete! Saved as final_model.keras")
