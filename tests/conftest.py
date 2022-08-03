import pytest

from ape import accounts


@pytest.fixture(scope="session")
def owner(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
def user(accounts):
    return accounts[1]
