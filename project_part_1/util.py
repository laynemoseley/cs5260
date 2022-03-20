import csv
import os
from genericpath import exists


def import_countries(test):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"tests/test-{test}-countries.csv")
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


def import_resource_info(test):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"tests/test-{test}-resources.csv")
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


# should be called once at the beginning of the test run to clear out the results
def reset_results(test):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"results/test-{test}-results.txt")
    if os.path.exists(filename):
        os.remove(filename)


# should be called everytime a new best schedule is found to update the results list
def update_results(test, schedule):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"results/test-{test}-results.txt")
    if exists(filename):
        file = open(filename)
    else:
        file = open(filename, "w+")

    contents = file.read()
    file.close()
    contents = f"""{schedule.print()} 
=====================================
=====================================
{contents}"""
    file = open(filename, "w+")
    file.write(contents)
    file.close()
