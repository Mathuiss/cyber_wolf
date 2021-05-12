#! /usr/bin/python3

import sys
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot

DATA_PATH = "/home/mathuis/Development/cyber_wolf/data"
MODEL_NAME = "best-model.h5"
HL_SIZE = 12

def load_data(path: str):
    print("Loading data")
    return np.load(path, allow_pickle=True)


def build_model():
    print("Building model")
    
    input_layer = layers.Input(shape=(98,))
    encoded = layers.Dense(HL_SIZE, activation="relu")(input_layer)
    decoded = layers.Dense(98, activation="relu")(encoded)

    model = keras.Model(input_layer, decoded)    

    return model

def train_model(model, x_train, x_test):
    print("Compiling model")
    model.compile(optimizer="adam", loss="mse", metrics=["mse", "msle", "mae", "mape", "cosine_similarity"])
    print("Training model")
    return model.fit(x_train, x_train, epochs=6, batch_size=32, validation_data=(x_test, x_test))

def main(arg):
    x_train = load_data(f"{DATA_PATH}/datasets/x_train.npy")
    x_test = load_data(f"{DATA_PATH}/datasets/x_test.npy")

    model = build_model()
    train_model(model, x_train, x_test)

    if arg == "save":
        model.save(f"{DATA_PATH}/models/{MODEL_NAME}")


if __name__ == "__main__":
    arg = ""

    if len(sys.argv) > 1:
        arg = sys.argv[1]

    main(arg)