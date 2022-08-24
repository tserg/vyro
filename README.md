# Vyro

An experimental [Vyper](https://github.com/vyperlang/vyper) to Cairo transpiler, inspired by [Warp](https://github.com/NethermindEth/warp) from Nethermind, and with a dash of [Brownie](https://github.com/eth-brownie/brownie).

## Installation

### Prequisites

#### Python

Vyro requires Python 3.7 to 3.9. Follow the instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

### Dependencies

Once you have your virtual environment set up and running, install Vyro with the following command:
```
pip install .[dev]
```

## Usage

### Transpile

To transpile a file, run the following command in your console:
```
vyro transpile FILENAME.vy
```

To print the output to console, run:
```
vyro transpile FILENAME.vy --print-output
```

To write the output to a file, run:
```
vyro transpile FILENAME.vy --output FILENAME.cairo
```

### Transform

To compile a Vyper file and print the Vyper AST to console, run the following command in your console:
```
vyro transform FILENAME.vy
```

### Testing (using Ape Framework)

To run the test suite, run the following command in your console:
```
ape test
```

To log the test output to console while running the test suite, run the following command in your console:
```
ape test -s
```

## Contributing

Feel free to submit a PR for bug fixes or to add a new feature.
