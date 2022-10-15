# Vyro

![tests](https://github.com/tserg/vyro/actions/workflows/test.yml/badge.svg)

A [Vyper](https://github.com/vyperlang/vyper) to Cairo transpiler, inspired by [Warp](https://github.com/NethermindEth/warp) from Nethermind, and with a dash of [Brownie](https://github.com/eth-brownie/brownie).

:exclamation: **This repository has not been audited or formally verified. Please use with caution.**

As this is a work in progress, there are numerous Vyper types (e.g. static arrays, dynamic arrays) and features that are not supported yet. Some features are also not capable of being supported on StarkNet. In these cases, the transpiler will throw an error.

## Getting started

### Dependencies

Vyro currently only supports Python 3.9 due to the Python version constraint of the libraries we rely on. Follow the instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

### Building from source

If you are building from source, either because you want to contribute or explore the codebase, we recommend you work within a virtual environment. Since we utilize [poetry](https://python-poetry.org/docs/#installation) as our dependency management system, you can easily setup your virtual environment by doing this at the root of the project:

```bash
poetry install
poetry run vyro
```

If you use pyenv for python version management, you may encounter some issues with getting the correct python version for your environment. If so, try the following:

```bash
pyenv shell 3.9.7 # Use a specific python version >=3.9 <3.10
poetry use python3 # Select this python version for your virtual env
# At this point a virtual environment should be created
poetry shell # Activate your virtual environment
```


### Installation

Since the distribution is currently not available via pip, you will have to clone this repository and install Vyro locally with the following command:

```
pip install .
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

You are most welcome to contribute! Feel free to submit a PR for improvements, bug fixes or to add a new feature.
