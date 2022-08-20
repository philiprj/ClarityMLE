import numpy as np
from tensorflow import keras
from pathlib import Path

if __name__ == "__main__":

    path = Path.cwd().joinpath("data")
    # Load the data and split it between train and test sets
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
    np.savez(path.joinpath("mnist_train.npz"), x=x_train, y=y_train)
    np.savez(path.joinpath("mnist_test.npz"), x=x_test, y=y_test)
