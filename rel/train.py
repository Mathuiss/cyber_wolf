#!/usr/bin/python

from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot
import numpy as np

DATA_PATH = "/home/mathuis/Downloads/cyber_wolf/data"
HL_SIZE = 8


def load_data(path: str):
    print("Loading data")
    return np.load(path, allow_pickle=True)


def build_model():
    print("Building model")

    input_layer = layers.Input(shape=(98,))
    encoded = layers.Dense(32, activation="relu")(input_layer)
    encoded = layers.Dense(HL_SIZE, activation="relu")(encoded)
    decoded = layers.Dense(32, activation="relu")(encoded)
    decoded = layers.Dense(98, activation="sigmoid")(decoded)

    model = keras.Model(input_layer, decoded)

    return model


def build_encoder():
    print("Building encoder")

    input_layer = layers.Input(shape=(98,))
    encoded = layers.Dense(HL_SIZE, activation="relu")(input_layer)

    encoder = keras.Model(input_layer, encoded)
    return encoder


def build_decoder():
    print("Building decoder")

    encoded_input = layers.Input(shape=(HL_SIZE,))
    decoded_layer = build_model().layers[-1]

    decoder = keras.Model(encoded_input, decoded_layer(encoded_input))
    return decoder


def train_model(model, x_train, x_test):
    print("Compiling model")
    model.compile(optimizer="adam",
                  loss="mean_squared_logarithmic_error", metrics=["accuracy"])
    print("Training model")
    return model.fit(x_train, x_train, epochs=7, validation_data=(x_test, x_test))


def plot(history):
    pyplot.subplot(211)
    pyplot.title("loss")
    pyplot.plot(history.history["loss"], label="train")
    pyplot.plot(history.history["val_loss"], label="test")
    pyplot.legend()

    pyplot.subplot(212)
    pyplot.title("accuracy")
    pyplot.plot(history.history["accuracy"], label="train")
    pyplot.plot(history.history["val_accuracy"], label="test")
    pyplot.legend()

    pyplot.show()


def evaluate_model(model, x_test):
    results = model.evaluate(x_test, x_test)
    print(f"Test Loss: {results}")


def main():
    # Load data from drive
    x_train = load_data(f"{DATA_PATH}/datasets/x_train.npy")
    x_test = load_data(f"{DATA_PATH}/datasets/x_test.npy")

    # Construct the model
    model = build_model()

    # Train the model
    history = train_model(model, x_train, x_test)

    # Plot results
    plot(history)

    # Evaluate model
    evaluate_model(model, x_test)

    # Test
    pred = model.predict(x_test[:1])
    print(x_test[1])
    print(pred[0])


if __name__ == "__main__":
    main()
