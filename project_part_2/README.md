# World Trade Simulation

## Requirements

- Python 3.9

## How to run

`python runner.py <test length in minutes>`

For example, if you would like to run each test for 5 minutes:

`python runner.py 5`

If an unknown test is supplied, test length will be 1 minutes.

## Tests

### Test 1

A race to get resources in order to build housing. Each country starts without the necessary resources to build any housing and must acquire the necessary resources through trade.

### Test 2

Like Test 1, but each country has enough resources to build housing immediately.

### Test 3

Each country already has housing and a small number of other resources. Housing and Electronics are equally weighted in importance.

## How to read results

Results are generated in the `results` folder with the appropriate name. Each best `schedule` that is found is contained within the file, with the first found at the bottom, and the most recent and best at the top.
