import os
import pandas as pd
import numpy

# Set data directory
data_path = "/home/mathuis/Downloads/cyber_wolf/data"

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


def extract_features(request):
    df = pd.DataFrame(columns=feature_def)

    for i in range(len(request)):
        frames = get_values(request, i)
        df = df.append(frames, ignore_index=True)

    return df


def get_values(request, i):
    df = pd.DataFrame(columns=feature_def)
    line = request[i]
    print(line)

    # In query
    if i == 0:
        values = split_query(line)
        df = df.append(histogram(values, "path"), ignore_index=True)

    # In header
    if line.contains(": "):
        values = split_header(line)
        df = df.append(histogram(values, "header"), ignore_index=True)

    # In body
    if line != "" and "" in request[:i]:
        values = split_body(line)
        df = df.append(histogram(values, "body"), ignore_index=True)

    return df


def split_query(line):
    if "?" not in line:
        return []

    querystring = line.split("?")[1]

    if "&" not in querystring:
        return list(querystring.split("=")[1])

    values = []
    sections = querystring.split("&")
    for section in sections():
        values.append(section.split("=")[1])

    return values


def split_header(line):
    return list(line.split(": "[1]))


def split_body(line):
    if "&" not in line:
        return list(line.split("=")[1])

    values = []
    parameters = line.split("&")
    for param in parameters:
        values.append(param.split("=")[1])


def histogram(values, location):
    for value in values:
        df = pd.DataFrame(columns=feature_def)
        # Set default values
        df.loc[0] = 0
        row = df.loc[0]
        row["length"] = len(value)
        row[location] = 1

        for char in value:
            row[char] += 1

    return df


def main():
    # Create base data frame
    df = pd.DataFrame(columns=feature_def)

    for file in os.listdir(data_path):
        # Read request contents
        file_contents = read_file_content(f"{data_path}/{file}")

        # Extract features from contents
        features = extract_features(file_contents)

        df = df.append(features, ignore_index=True)

    print(df)


if __name__ == "__main__":
    main()
