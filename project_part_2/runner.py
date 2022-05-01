from util import clear_results_folder, prepare_csv_results, append_csv_result
from simulation import run_simulation

# 10 seconds, 1 minute, 10 minutes]
timeouts = [0.167, 1, 10]
tests = ["1", "2", "3"]
frontier_sizes = [5, 50, 500, 5000, 50000, 500000]

clear_results_folder()

for timeout in timeouts:
    print(f"Simulation starting with timeout of {timeout} minutes per test")
    prepare_csv_results(timeout)

    for test in tests:
        print(f"Starting test with dataset {test}")

        for frontier_size in frontier_sizes:
            print(f"Frontier size {frontier_size}")
            result = run_simulation(test, timeout, frontier_size, "best_first")
            append_csv_result(timeout, result)
