import csv
import os
import glob
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


def result_file_with_name(name):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, f"results/{name}")


def clear_results_folder():
    folder = result_file_with_name("*")
    files = glob.glob(folder)
    for f in files:
        os.remove(f)


# should be called once at the beginning of the test run to clear out the results
def reset_results(test_name):
    path = result_file_with_name(f"test-{test_name}-results.txt")
    if os.path.exists(path):
        os.remove(path)


# should be called everytime a new best schedule is found to update the results list
def update_results(test_name, schedule):
    prepend_results_to_test(test_name, schedule.print())


def finish_results(test_name, search_result):
    contents = f"""Search Finished!
depth reached: {search_result.depth_reached}
frontier size: {search_result.frontier_size}
search type: {search_result.search_type}
best score: {search_result.best_score}
seconds taken: {search_result.seconds_elapsed}
successor count: {search_result.node_count}"""
    prepend_results_to_test(test_name, contents)


def prepend_results_to_test(test_name, new_contents):
    filename = result_file_with_name(f"test-{test_name}-results.txt")
    if exists(filename):
        file = open(filename)
    else:
        file = open(filename, "w+")

    contents = file.read()
    file.close()
    contents = f"""{new_contents} 
=====================================
=====================================
{contents}"""
    file = open(filename, "w+")
    file.write(contents)
    file.close()


def prepare_csv_results(timeout):
    path = result_file_with_name(f"results-{timeout}.csv")
    file = open(path, "w+")
    file.write("data set,frontier size,seconds elapsed,best score,successor count,max depth reached\n")
    file.close()


def append_csv_result(timeout, search_result):
    path = result_file_with_name(f"results-{timeout}.csv")
    file = open(path, "at")

    file.write(
        f"{search_result.data_set},{search_result.frontier_size},{search_result.seconds_elapsed:.1f},{search_result.best_score:.5f},{search_result.node_count},{search_result.depth_reached}\n"
    )
    file.close()
