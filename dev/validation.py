#!/usr/bin/python3

import os
from tensorflow import keras
from tensorflow.keras.models import load_model
import preprocessor

ADVERSARIAL_PATH = "/home/mathuis/Development/cyber_wolf/data/adversarial"
MODEL_PATH = "/home/mathuis/Development/cyber_wolf/data"
MODEL_NAME = "1h-13n-5e-b32-notnorm-model.h5"


def get_values_plaintext(request, i):
    line = request[i].strip()

    values = []

    # In query
    if i == 0:
        values = preprocessor.split_query(line)

    # In header
    if ": " in line:
        values = preprocessor.split_header(line)

    # In body
    if line != "\n" and "\n" in request[0:i]:
        values = preprocessor.split_body(line)

    return values


model = load_model(f"{MODEL_PATH}/models/{MODEL_NAME}")
preprocessor.load_ignorefile()

for file_name in os.listdir(ADVERSARIAL_PATH):
    values = []
    request = preprocessor.read_file_content(f"{ADVERSARIAL_PATH}/{file_name}")

    for i in range(len(request)):
        arr_val = get_values_plaintext(request, i)
        for val in arr_val:
            values.append(val)

    features = preprocessor.preprocess(request)

    print("###### EVALUATION WHOLE #######")
    print(file_name)
    model.evaluate(features, features)


    for i in range(len(values)):
        x_row = features[i]
        val = values[i]

        x = x_row.reshape((-1,98))

        print(val)
        e = model.evaluate(x, x)
