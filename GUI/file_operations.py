import numpy as np
import yaml

def load_txt(filename: str):
    with open(filename) as file:
        lines = file.readlines()
        splitted = [line.split(" ", 1) for line in lines]
        return [(float(value_pair[0]), float(value_pair[1])) for value_pair in splitted]
    
def save_array(arr, filename):  # only works for txt file
    with open(filename, "w") as file:
        for x, y in arr:
            file.write(f"{x} {y}\n")

# Based on https://python.land/data-processing/python-yaml (12.05.2024)
def load_settings(settings_filename: str = "settings.yaml"):
    with open(settings_filename, 'r') as file:
        return yaml.safe_load(file)