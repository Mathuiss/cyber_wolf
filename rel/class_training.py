#! /usr/bin/python3

import sys
import numpy as np
import config
from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot

dataset_path = config.read_value("dataset_path")
model_path = config.read_value("model_path")
model_name = config.read_value("model_name")
# MODEL_NAME = "1h-4n-e20-b64-class-model.h5"

HL_SIZE = 4

def load_data(path: str):
    print("Loading data")
    return np.load(path, allow_pickle=True)


def build_model():
    print("Building model")
    
    input_layer = layers.Input(shape=(48,))
    encoded = layers.Dense(HL_SIZE, activation="relu")(input_layer)
    decoded = layers.Dense(48, activation="relu")(encoded)

    model = keras.Model(input_layer, decoded)    

    return model

def train_model(model, x_train, x_test):
    print("Compiling model")
    model.compile(optimizer="adam", loss="mse", metrics=["mse", "msle", "mae", "mape", "cosine_similarity"])
    print("Training model")
    return model.fit(x_train, x_train, epochs=20, batch_size=64, validation_data=(x_test, x_test))

def plot(history):
    print(history.keys())

    for key in history.keys():
        if not key.startswith("val_"):
            pyplot.plot()

            pyplot.title(key)
            pyplot.plot(history[key], label="train")
            pyplot.plot(history[f"val_{key}"], label="test")
            pyplot.xlabel("Epoch")
            pyplot.ylabel(key)
            pyplot.legend()

            pyplot.show()

def main(arg):
    x_train = load_data(f"{dataset_path}/class_x_train.npy")
    x_test = load_data(f"{dataset_path}/class_x_test.npy")

    model = build_model()
    res = train_model(model, x_train, x_test)
    plot(res.history)

    if arg == "save":
        model.save(f"{model_path}/{model_name}")


if __name__ == "__main__":
    arg = ""

    if len(sys.argv) > 1:
        arg = sys.argv[1]

    main(arg)