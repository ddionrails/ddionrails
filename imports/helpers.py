import csv
import os


def read_csv(filename, path=None):
    """
    Generic function to import a CSV file and return it as a dict.
    """
    if path:
        filename = os.path.join(path, filename)
    with open(filename, "r") as file:
        content = [row for row in csv.DictReader(file)]
    return content
