#!/usr/bin/python3

import os
from tensorflow import keras
from tensorflow.keras.models import load_model
from config import read_value
import preprocessor
import numpy as np

ADVERSARIAL_PATH = "/home/mathuis/Development/cyber_wolf/data/adversarial"
MODEL_PATH = "/home/mathuis/Development/cyber_wolf/data"
# MODEL_NAME = "1h-12n-6e-b32-mse_loss-notnorm-model.h5"
MODEL_NAME = "best-model.h5"

epsilon = float(read_value("epsilon"))

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

def parse(request):
    values = []

    for i in range(len(request)):
        arr_val = get_values_plaintext(request, i)
        for val in arr_val:
            values.append(val)
    
    return values

def evaluate(values, features):
    list_mse = []

    for i in range(len(values)):
        x_row = features[i]
        val = values[i]

        x = x_row.reshape((-1,98))

        print(val)
        e = model.evaluate(x, x)
        list_mse.append(e[0])

    return list_mse

def show_results(values, list_mse, mean, std_dev, threshf, threshb):
    print("#################################################")
    print(f"AVG MSE: {mean}")
    print(f"STD DEV: {std_dev}")
    print(f"THRESHF: {threshf}")
    print(f"THRESHB: {threshb}")
    print("#################################################")

    for i in range(len(values)):
        if std_dev <= epsilon:
            continue

        if list_mse[i] >= threshb:
            print(f"BLOCKED: {values[i]}")
            continue

        if list_mse[i] >= threshf:
            print(f"FLAGGED: {values[i]}")
            continue


model = load_model(f"{MODEL_PATH}/models/{MODEL_NAME}")
preprocessor.load_ignorefile()

for file_name in os.listdir(ADVERSARIAL_PATH):
    print("#################################################")
    print(file_name)
    print("#################################################")

    request = preprocessor.read_file_content(f"{ADVERSARIAL_PATH}/{file_name}")
    values = parse(request)
    features = preprocessor.preprocess(request)
    list_mse = evaluate(values, features)

    mean = sum(list_mse) / len(list_mse)
    std_dev = np.std(list_mse)
    threshold_flag = mean + std_dev
    threshold_block = threshold_flag + std_dev

    show_results(values, list_mse, mean, std_dev, threshold_flag, threshold_block)