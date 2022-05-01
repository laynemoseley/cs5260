# World Trade Simulation

## Requirements

- Python 3.9

## How to run

`python runner.py`

## Modify the test parameters

`runner.py` contains the test parameters at the top of the file after the imports. If other tests should be run, `runner.py` can be modified directly.

## Tests

### Test 1

A race to get resources in order to build housing. Each country starts without the necessary resources to build any housing and must acquire the necessary resources through trade.

### Test 2

Like Test 1, but each country has enough resources to build housing immediately.

### Test 3

Each country already has housing and a small number of other resources. Housing and Electronics are equally weighted in importance.

## How to read results

Results are generated in the `results` folder with the appropriate name. Each best `schedule` that is found is contained within the file, with the first found at the bottom, and the most recent and best at the top.
