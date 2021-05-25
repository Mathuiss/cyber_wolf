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
                return sp[1].rstrip()

        raise Exception(f"Key {key} not found in config file.")

def append_flags(values, path="cyberwolf.flags"):
    with open(path, "r") as f:
        flags = f.readlines()

        for value in values:
            if value not in flags:
                flags.append(value)

        with open(path, "w") as w:
            for flag in flags:
                w.write(f"{flag}\n")