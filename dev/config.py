# Read the configuration file and return the value for the given key
def read_value(key, path="cyberwolf.config"):
    with open(path, "r") as f:
        lines = f.readlines()

        for line in lines:
            if line.startswith("#"):
                continue

            if not line:
                continue

            sp = line.split("=")
            k = sp[0]

            if k == key:
                return sp[1]

        raise Exception(f"Key {key} not found in config file.")