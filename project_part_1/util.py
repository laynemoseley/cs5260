import csv
from itertools import count
import os

def import_countries():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'example-countries.csv')
    file = open(filename)
    print(file)
    reader = csv.reader(file)
    headers = None
    countries = []
    for row in reader:
        if headers is None:
            headers = row
        else:
            country = {}
            for i, header in enumerate(headers):
                country[header] = row[i]
            countries.append(country)
    return countries