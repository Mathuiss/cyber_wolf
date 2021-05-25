#!/usr/bin/python3

import os
import pandas as pd
import numpy as np

# Set data directory
DATA_PATH = "/home/mathuis/Development/cyber_wolf/data"

# Set path to ignore file
IGNORE_FILE = "/home/mathuis/Development/cyber_wolf/data/value_ignore.txt"

# Set feature definition
FEATUE_DEF = ["path", "header", "body", "length", "a", "b", "c", "d", "e", "f", "g", "h", "i",
              "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
              "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
              "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7",
              "8", "9", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "!", "\"", "#", "$", "%",
              "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", ">", "=", "?", "@"]

TEST_RATIO = 0.2

ignore_keys = []

def load_ignorefile():
    global ignore_keys
    ignore_keys = read_file_content(IGNORE_FILE)

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

            row[char] += 1

        req_df = req_df.append(df, ignore_index=True)

    return req_df


# Normalizes the correct values
# def normalize(df):
#     # Normalize histogram
#     # The normalized count is the count in a class divided by the total number of observations.
#     # In this case the relative counts are normalized to sum to one (or 100 if a percentage scale is used).
#     # This is the intuitive case where the height of the histogram bar represents the proportion of the data in each class.

#     # Calculate the sum for each column
#     # Calculate normalized ratio based on sum for each row and col in base dataframe
#     for col in NORM_COLS:
#         print(f"Normalizing: {col}")
#         if df[col].sum() != 0:
#             df[col] = df.apply(lambda x: x[col] / df[col].sum(), axis=1)

#         print(f"Total: {df[col].sum()}")

#     return df


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

    files = os.listdir(f"{DATA_PATH}/requests")

    print(f"Preprocessing {len(files)} requests")

    for file in files:
        # Read request contents
        file_contents = read_file_content(f"{DATA_PATH}/requests/{file}")

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
    df.to_csv(f"{DATA_PATH}/datasets/notnorm_dataset.csv")
    np.save(f"{DATA_PATH}/datasets/notnorm_x_train", x_train)
    np.save(f"{DATA_PATH}/datasets/notnorm_x_test", x_test)


if __name__ == "__main__":
    main()
