import json

def write_json(data, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(data))

def read_json(filename):
    with open(filename, "r") as f:
        return json.load(f)