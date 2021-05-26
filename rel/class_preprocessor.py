#!/usr/bin/python3

import os
import pandas as pd
import numpy as np
import config

# Set data directory
dataset_path = config.read_value("dataset_path")

request_path = config.read_value("request_path")

# Set path to ignore file
ignore_file = config.read_value("ignore_file")


FEATUE_DEF = ["path", "header", "body", "length", "lowercase", "uppercase", "0", "1", "2", "3", "4", "5", "6", "7",
            "8", "9", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "!", "\"", "#", "$", "%",
            "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", ">", "=", "?", "@"]

LOWERCASE_LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q",
                "r", "s", "t", "u", "v", "w", "x", "y", "z"]

CAPITAL_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                    "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

TEST_RATIO = 0.2

ignore_keys = []

def load_ignorefile():
    global ignore_keys
    ignore_keys = read_file_content(ignore_file)

    for i in range(len(ignore_keys)):
        ignore_keys[i] = ignore_keys[i].strip().strip("\n").strip("\r").lower()

# Reads a file and returns the lines as an array
def read_file_content(data_path):
    with open(data_path, "r") as f:
        return f.readlines()


# Loops through lines in request
# Appends results tot base dataframe
def extract_features(request):
    df = pd.DataFrame(columns=FEATUE_DEF)

    for i in range(len(request)):
        frames = get_values(request, i)
        df = df.append(frames, ignore_index=True)

    return df


# Gets the features from the line
# Returns features, appended to the base dataframe
def get_values(request, i):
    df = pd.DataFrame(columns=FEATUE_DEF)
    line = request[i].strip()

    # In query
    if i == 0:
        values = split_query(line)
        df = df.append(histogram(values, "path"), ignore_index=True)

    # In header
    if ": " in line:
        values = split_header(line)
        df = df.append(histogram(values, "header"), ignore_index=True)
        # return df

    # In body
    if line != "\n" and "\n" in request[0:i]:
        values = split_body(line)
        df = df.append(histogram(values, "body"), ignore_index=True)

    return df


# Parses query values
def split_query(line):
    line = line.split(" ")[1]

    print(line)

    if "?" not in line:
        return []

    querystring = line.partition("?")[2]

    if len(querystring) == 0:
        return []

    if "&" not in querystring:
        sp = querystring.partition("=")
        if sp[0].lower() not in ignore_keys:
            return [sp[2]]
        else:
            return []

    values = []
    sections = querystring.split("&")
    for section in sections:
        sp = section.partition("=")
        if len(sp) > 2:
            if sp[0].lower() not in ignore_keys:
                values.append(sp[2])

    return values


# Parses header values
def split_header(line):
    sp = line.split(": ")
    if sp[0].lower() not in ignore_keys:
        return [sp[1]]
    else:
        return []


# Parses body values
def split_body(line):
    if "&" not in line:
        sp = line.partition("=")
        if len(sp) > 2:
            if sp[0].lower() not in ignore_keys:
                return [sp[2]]
            else:
                return []
        else:
            return []

    values = []
    parameters = line.split("&")
    for param in parameters:
        sp = param.partition("=")
        if len(sp) > 2:
            if sp[0].lower() not in ignore_keys:
                values.append(sp[2])

    return values


# Generates the row in the dataframe
# Builds histogram of the data
def histogram(values, location):
    req_df = pd.DataFrame(columns=FEATUE_DEF)

    for value in values:
        df = pd.DataFrame(columns=FEATUE_DEF)
        # Set default values
        df.loc[0] = 0
        row = df.loc[0]
        row["length"] = len(value)
        row[location] = 1

        for char in value:
            if char == " ":
                continue

            if char in LOWERCASE_LETTERS:
                row["lowercase"] += 1
                continue

            if char in CAPITAL_LETTERS:
                row["uppercase"] += 1
                continue

            row[char] += 1

        req_df = req_df.append(df, ignore_index=True)

    return req_df


def preprocess(request):
    load_ignorefile()
    x = extract_features(request)
    x = np.asarray(x).astype("float32")

    return x

def main():
    # Set ignore values
    load_ignorefile()

    # Create base data frame
    df = pd.DataFrame(columns=FEATUE_DEF)

    files = os.listdir(request_path)

    print(f"Preprocessing {len(files)} requests")

    for file in files:
        # Read request contents
        file_contents = read_file_content(f"{request_path}/{file}")

        # Extract features from contents
        features = extract_features(file_contents)

        # Add data to the base dataframe
        df = df.append(features, ignore_index=True)

    # Shuffle random
    df = df.sample(frac=1).reset_index(drop=True)

    # We will not normalize the dataset
    # When normalizing, the entire range of the training dataset is considered
    # In a practical situation, when normalizing a new request, the ranges will differ from the training dataset
    # df = normalize(df)

    print(df)

    # Calculate the training set size
    train_count = int(len(df) - len(df) * TEST_RATIO)

    x_train = df[0:train_count].to_numpy()
    x_test = df[train_count:len(df) + 1].to_numpy()

    x_train = np.asarray(x_train).astype("float32")
    x_test = np.asarray(x_test).astype("float32")

    # Save complete dataset to csv
    df.to_csv(f"{dataset_path}/class_dataset.csv")
    np.save(f"{dataset_path}/class_x_train", x_train)
    np.save(f"{dataset_path}/class_x_test", x_test)


if __name__ == "__main__":
    main()
