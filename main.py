from Solver import Solver
from Parser import Parser

def load_config(path):
    config = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#') and line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

config = load_config("C:/Config/config.txt")

connection = Solver(solver=config["solver"])

parser = Parser(connection, config)

parser.hand_by_spot = 150
parser.make()
parser.save()