import pytest
import os
from pathlib import Path

from ape import Project, networks

from tests.expectations import EXPECTATIONS
from tests.utils import transpile_to_cairo


# Loop through expectations

# Fetch the file name

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

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        call_args = c[1]
        expected = c[2]

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
    expected_cairo_file_path = f"examples/{filename}_transpiled.cairo"
    transpile_to_cairo(file_path, expected_cairo_file_path)

    assert os.path.exists(expected_cairo_file_path) == True


# Perform tests in cairo
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_cairo_code(project, starknet_user, code):
    """
    Test Cairo code against expectations.
    """
    filename = f"{code[0]}_transpiled"
    file_path = Path(f"examples/{filename}.cairo")

    contract_object = getattr(project, filename)

    # Obtain the `ContractInstance`
    with networks.starknet.local.use_provider("starknet"):
        contract = contract_object.deploy()

        test_cases = code[1]
        for c in test_cases:
            function_name = c[0]
            call_args = c[1]
            expected = c[2]

            fn_call = getattr(contract, function_name)

            if expected is None:
                fn_call(*call_args, sender=starknet_user)

            else:
                assert fn_call(*call_args) == expected
