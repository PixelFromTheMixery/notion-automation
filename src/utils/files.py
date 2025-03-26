import yaml


def write_yaml(data, filename):
    with open(filename, "w") as f:
        f.write(yaml.dump(data))


def read_yaml(filename):
    with open(filename, "r") as f:
        return yaml.safe_load(f)
