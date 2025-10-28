import numpy as np
import tensorflow as tf
import cv2
from tensorflow.keras.preprocessing import image

def generate_gradcam(model, img_path, output_path="uploads/gradcam_result.jpg", layer_name=None):
    """
    Generates and saves a Grad-CAM heatmap overlay for the input image.
    Compatible with TensorFlow 2.x and Keras 3.x.
    """
    # Load and preprocess image
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    # Predict class
    preds = model(img_array)
    class_index = tf.argmax(preds[0])
    class_output = preds[:, class_index]

    # Automatically detect the last conv layer if not specified
    if layer_name is None:
        for layer in reversed(model.layers):
            if len(layer.output_shape) == 4:
                layer_name = layer.name
                break

    # Build a model that maps input to activations and predictions
    grad_model = tf.keras.models.Model(
        [model.inputs], 
        [model.get_layer(layer_name).output, model.output]
    )

    # Compute the gradient of the predicted class wrt last conv output
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)

    # Normalize the heatmap between 0–1
    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1
    heatmap = cv2.resize(heatmap.numpy(), (224, 224))

    # Overlay heatmap on original image
    original = cv2.imread(img_path)
    original = cv2.resize(original, (224, 224))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    superimposed = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)

    # Save final Grad-CAM image
    cv2.imwrite(output_path, superimposed)
    return output_path
