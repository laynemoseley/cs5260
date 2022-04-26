import sys

from simulation import run_simulation

timeout = 1
if len(sys.argv) > 1:
    input = sys.argv[1]
    try:
        timeout = int(input)
    except:
        pass

print(f"Simulation starting with timeout of {timeout} minutes per test")
tests = ["1", "2", "3"]
frontier_size_tests = [100, 1000, 10000]
for test in tests:
    for frontier_size in frontier_size_tests:
        print(
            "HIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHIHI"
        )
        run_simulation(test, timeout, frontier_size, "best_first")
