import os
import pandas as pd
import numpy

# Set data directory
data_path = "../data"

# Set feature definition
feature_def = ["path", "header", "body", "length", "a", "b", "c", "d", "e", "f", "g", "h", "i",
               "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
               "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
               "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7",
               "8", "9", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "!", "\"", "#", "$", "%",
               "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", ">", "=", "?", "@"]


def read_file_content(data_path):
    with open(data_path, "r") as f:
        return f.readlines()


def extract_features(df, request):
    for i in range(len(request)):
        values = get_values(df, request, i)

        for value in values:
            df = histogram(df, value)

    return df


def get_values(df, request, i):
    # Set default values
    index = len(df) + 1
    row = df.loc[index]
    row = 0

    print(row)

    line = request[i]
    print(line)

    if i == 0:
        return split_query()

    if line.contains(": ")
    return split_header()


def histogram(df, values):

    return df


def main():
    # Create base data frame
    df = pd.DataFrame(columns=feature_def)

    for file in os.listdir(data_path):
        # Read request contents
        file_contents = read_file_content(f"{data_path}/{file}")

        # Extract features from contents
        features = extract_features(df, file_contents)


if __name__ == "__main__":
    main()
