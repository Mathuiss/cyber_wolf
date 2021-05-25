#!/usr/bin/python3

import os
from tensorflow import keras
from tensorflow.keras.models import load_model
from config import read_value, append_flags
import class_preprocessor
import numpy as np

adversarial_path = read_value("adversarial_path")
model_path = read_value("model_path")
# MODEL_NAME = "1h-4n-e20-b64-class-model.h5"
model_name = read_value("model_name")

epsilon = float(read_value("epsilon"))
threshd = float(read_value("threshd"))

def get_values_plaintext(request, i):
    line = request[i].strip()

    values = []

    # In query
    if i == 0:
        values = class_preprocessor.split_query(line)

    # In header
    if ": " in line:
        values = class_preprocessor.split_header(line)

    # In body
    if line != "\n" and "\n" in request[0:i]:
        values = class_preprocessor.split_body(line)

    return values

def parse(request):
    values = []

    for i in range(len(request)):
        arr_val = get_values_plaintext(request, i)
        for val in arr_val:
            values.append(val)
    
    return values

def evaluate(model, values, features):
    list_mse = []

    for i in range(len(values)):
        x_row = features[i]
        val = values[i]

        x = x_row.reshape((-1,48))

        print(val)
        e = model.evaluate(x, x)
        list_mse.append(e[0])

    return list_mse

def show_results(values, list_mse, mean, std_dev, threshf, threshb):
    print("################## EVALUATION ###################")
    print(f"AVG MSE: {mean}")
    print(f"STD DEV: {std_dev}")
    print(f"THRESHF: {threshf}")
    print(f"THRESHB: {threshb}")
    print("#################################################")

    if std_dev <= threshd:
        return

    for i in range(len(values)):

        if list_mse[i] >= threshb:
            print(f"BLOCKED: {values[i]}")
            continue

        if list_mse[i] >= threshf:
            print(f"FLAGGED: {values[i]}")
            continue

def validate(model, values, features):
    list_mse = evaluate(model, values, features)

    # Get the average MSE
    mean = sum(list_mse) / len(list_mse)
    # Get the standard deviation of the list
    std_dev = np.std(list_mse)
    # Get the flag threshold (mean + 1 * std dev)
    threshf = mean + std_dev
    # Get the block threshold (mean + 2 * std dev)
    threshb = threshf + (epsilon * std_dev)

    # Show results
    show_results(values, list_mse, mean, std_dev, threshf, threshb)

    if std_dev <= threshd:
        return True
    
    flags = []

    for i in range(len(values)):
        if list_mse[i] >= threshb:
            return False

        if list_mse[i] >= threshf:
            flags.append(values[i])
            continue

    append_flags(flags)

    return True



def main():
    model = load_model(f"{model_path}/{model_name}")
    class_preprocessor.load_ignorefile()

    total_len = 0

    for file_name in os.listdir(adversarial_path):
        print("#################################################")
        print(file_name)
        print("#################################################")

        request = class_preprocessor.read_file_content(f"{adversarial_path}/{file_name}")
        values = parse(request)
        features = class_preprocessor.preprocess(request)
        list_mse = evaluate(model, values, features)

        total_len += len(list_mse)

        mean = sum(list_mse) / len(list_mse)
        std_dev = np.std(list_mse)
        threshold_flag = mean + std_dev
        threshold_block = threshold_flag + (epsilon * std_dev)

        show_results(values, list_mse, mean, std_dev, threshold_flag, threshold_block)

    print(f"TOTAL LEN: {total_len}")

if __name__ == "__main__":
    main()