import numpy as np
from tensorflow.keras.utils import get_file, load_img, img_to_array
import tensorflow as tf
from tensorflow.nn import softmax
from typing import Union

# from tensorflow import keras


def NormalizeData(data: Union[np.array, tf.Tensor]) -> Union[np.array, tf.Tensor]:
    return (data - np.min(data)) / (np.max(data) - np.min(data))


def preprocess(image_link: str) -> tf.Tensor:
    """Takes link to an image data

    Args:
        image_link (str): Link to image data

    Returns:
        img (tf.Tensor): Tensorflow tensor of the image
    """
    # Read file from link
    img_path = get_file(origin=image_link)
    # Load image and resize and colour
    img = load_img(img_path, target_size=(28, 28), color_mode="grayscale")
    # Convert to arrat
    img_array = img_to_array(img, dtype="float32")
    # Expand dimensions for input shape
    img_array = tf.expand_dims(img_array, 0)
    # Nomralise [0, 1]
    img_array = NormalizeData(img_array)
    return img_array


def preprocess_batch(images: list) -> tf.Tensor:
    """In a list of batch images, processes them and returns a tensor

    Args:
        images (list): List of numerical image data

    Returns:
        img (tf.Tensor): Tensorflow tensor of the image
    """
    # Convert list to tf.Tensor
    img = tf.convert_to_tensor(images, dtype="float32")
    # Load image and resize and colour
    img = tf.image.resize(img, size=(28, 28))
    if img.shape[-1] != 1:
        img = tf.image.rgb_to_grayscale(img)
    # Expand dimensions for input shape
    if len(img.shape) == 3:
        img = tf.expand_dims(img, 0)
    # Nomralise [0, 1]
    img = NormalizeData(img)
    return img


def predict(model, image: Union[np.array, tf.Tensor]) -> Union[np.array, tf.Tensor]:
    """Predict image using model

    Args:
        model: Compiled keras model object
        image (np.array | tf.Tensor): Image array

    Returns:
        (np.array): Array of predicted labels
    """
    pred = model.predict(image)
    score = softmax(pred)
    return np.argmax(score, axis=1)
