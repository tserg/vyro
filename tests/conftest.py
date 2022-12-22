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
def eth_guest(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def starknet_devnet_accounts():
    yield accounts.containers["starknet"].test_accounts


@pytest.fixture(scope="session")
def starknet_owner(starknet_devnet_accounts):
    yield starknet_devnet_accounts[0]


@pytest.fixture(scope="session")
def starknet_user(starknet_devnet_accounts):
    yield starknet_devnet_accounts[1]


@pytest.fixture(scope="session")
def starknet_guest(starknet_devnet_accounts):
    yield starknet_devnet_accounts[2]


@pytest.fixture(scope="session")
def starknet_devnet(networks):
    with networks.parse_network_choice("starknet:local"):
        yield


def pytest_sessionfinish(session, exitstatus):
    # Remove all transpiled .cairo files in examples directory
    examples_dir = os.listdir("examples")
    for i in examples_dir:
        if i.endswith(".cairo"):
            os.remove(f"examples/{i}")

    print("\n\n=============== Deleted transpiled Cairo files ===============")


@pytest.fixture
def assert_transpile_failed():
    def assert_transpile_failed(function_to_test, exception=Exception):
        with pytest.raises(exception):
            function_to_test()

    return assert_transpile_failed
