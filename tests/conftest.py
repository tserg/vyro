import os
import pytest

from ape import accounts


@pytest.fixture(scope="session")
def owner(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def user(accounts):
    return accounts[1]


def pytest_sessionfinish(session, exitstatus):
    # Remove all transpiled .cairo files in examples directory
    examples_dir = os.listdir("examples")
    for i in examples_dir:
        if i.endswith(".cairo"):
            os.remove(f"examples/{i}")

    print("\n\n=============== Deleted transpiled Cairo files ===============\n\n")
