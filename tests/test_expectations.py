import pytest
import os

from tests.expectations import EXPECTATIONS
from tests.utils import transpile_to_cairo


# Perform tests in vyper
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_vyper_code(project, eth_owner, eth_user, code):
    """
    Test Vyper code against expectations.
    """
    filename = code[0]
    contract_object = getattr(project, filename)

    # Obtain the `ContractInstance`
    contract = eth_owner.deploy(contract_object)

    print(f"Testing Vyper contract: {filename}.vy")

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        call_args = c[1]
        expected = c[2]

        print(f"Testing function: {function_name}")
        fn_call = getattr(contract, function_name)

        if expected is None:
            fn_call(*call_args, sender=eth_user)

        else:
            assert fn_call(*call_args, sender=eth_user) == expected


# Transpile and output cairo to same folder
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_transpile(code):
    """
    Test transpilation of Vyper file to Cairo.
    """
    filename = code[0]
    file_path = f"examples/{filename}.vy"
    print(f"Transpiling Vyper contract: {filename}.vy")

    expected_cairo_file_path = f"examples/{filename}_transpiled.cairo"
    transpile_to_cairo(file_path, expected_cairo_file_path)

    assert os.path.exists(expected_cairo_file_path) is True


# Perform tests in cairo
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_cairo_code(project, starknet_devnet, starknet_user, code):
    """
    Test Cairo code against expectations.
    """
    filename = f"{code[0]}_transpiled"
    contract_object = getattr(project, filename)

    # Obtain the `ContractInstance`
    # with networks.starknet.local.use_provider("starknet"):
    contract = contract_object.deploy()

    print(f"Testing Cairo contract: {filename}.cairo")

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        call_args = c[1]
        expected = c[2]

        print(f"Testing function: {function_name}")
        fn_call = getattr(contract, function_name)

        if expected is None:
            fn_call(*call_args, sender=starknet_user)

        else:
            assert fn_call(*call_args) == expected
