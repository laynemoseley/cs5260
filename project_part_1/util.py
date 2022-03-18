import csv
from itertools import count
import os


def import_countries():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "example-countries.csv")
    file = open(filename)
    reader = csv.reader(file)
    headers = None
    countries = []
    for row in reader:
        if headers is None:
            headers = row
        else:
            country = {}
            for i, header in enumerate(headers):
                if header != "Country":
                    country[header] = int(row[i])
                else:
                    country[header] = row[i]
            countries.append(country)
    return countries


def import_resource_info():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "example-resources.csv")
    file = open(filename)
    reader = csv.reader(file)
    headers = None
    weights = {}
    for row in reader:
        if headers is None:
            headers = row
        else:
            weights[row[0]] = {"weight": float(row[1]), "notes": row[2]}

    return weights
