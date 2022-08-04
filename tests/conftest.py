import os
import pytest

from ape import accounts


@pytest.fixture(scope="session")
def eth_owner(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def eth_user(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def starknet_devnet_accounts():
    yield accounts.containers["starknet"].test_accounts


@pytest.fixture(scope="session")
def starknet_owner(starknet_devnet_accounts):
    yield starknet_devnet_accounts[0]


@pytest.fixture(scope="session")
def starknet_user(starknet_devnet_accounts):
    yield starknet_devnet_accounts[1]


def pytest_sessionfinish(session, exitstatus):
    # Remove all transpiled .cairo files in examples directory
    examples_dir = os.listdir("examples")
    for i in examples_dir:
        if i.endswith(".cairo"):
            os.remove(f"examples/{i}")

    print("\n\n=============== Deleted transpiled Cairo files ===============\n\n")
