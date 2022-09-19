import cv2
import numpy as np
import os
import sys

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []
    # recursively iterate directories for files
    for root, subdirs, files in os.walk(data_dir):
        for filename in files:
            img_path = os.path.join(root, filename)
            # get label
            label = int(os.path.basename(root))
            # load image
            img = cv2.imread(img_path, cv2.IMREAD_COLOR)
            # resize image
            img = resize_image(img, img_width=IMG_WIDTH, img_height=IMG_HEIGHT)
            # append to the list
            images.append(img)
            labels.append(label)
    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # Create a neural network
    model = Sequential()
    # Add convolutional layer with 32 filters using 3x3 kernel
    model.add(Conv2D(32, (3,3), activation="relu",  input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)))
    model.add(Conv2D(32, (3,3), activation="relu"))
    model.add(Conv2D(32, (3,3), activation="relu"))
    # Add max-pooling layer using 2x2 pool size
    model.add(MaxPooling2D(pool_size=(2, 2)))
    # Flatten
    model.add(Flatten())
    # Add a 3 hidden layers with 128 units, with ReLU activation + add 50/50/25% dropout
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.50))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.50))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.25))
    # Add output layer, with softmax activation
    model.add(Dense(NUM_CATEGORIES, activation="softmax"))

    # Compile neural network
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def resize_image(img, img_width=30, img_height=30):
    """
    Resizes image.
    """
    return cv2.resize(img, (img_width, img_height))


if __name__ == "__main__":
    main()
