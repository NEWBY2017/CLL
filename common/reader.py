import json

def csv_reader(fp):
    data = []
    with open(fp) as file:
        for line in file:
            data.append(line.strip("\n").split(","))
    return data

def csv_generator(fp):
    with open(fp) as file:
        for line in file:
            yield line.strip("\n").split(",")

def json_reader(fp):
    data = []
    with open(fp, "r") as file:
        for line in file:
            data.append(json.loads(line))
    return data

def json_generator(fp):
    with open(fp) as file:
        for line in file:
            yield json.loads(line)
