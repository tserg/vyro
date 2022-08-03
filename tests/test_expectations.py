import pytest
import os

from ape import Project

from tests.expectations import EXPECTATIONS


# Loop through expectations

# Fetch the file name

# Perform tests in vyper

@pytest.mark.parametrize("code", EXPECTATIONS)
def test_vyper_code(project, owner, user, code):
    """
    Test Vyper code against expectations.
    """
    filename = code[0]
    contract_object = getattr(project, filename)

    # Obtain the `ContractInstance`
    contract = owner.deploy(contract_object)

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        call_args = c[1]
        expected = c[2]

        fn_call = getattr(contract, function_name)

        if expected is None:
            fn_call(*call_args, sender=user)

        else:
            assert fn_call(*call_args, sender=user) == expected

# Transpile and output cairo to same folder

# Perform tests in cairo


@pytest.mark.parametrize("code", EXPECTATIONS)
def test_transpile(code):
    """
    Test transpilation of Vyper file to Cairo.
    """
    filename = code[0]
    file_path = f"examples/{filename}.vy"
    expected_cairo_file_path = f"examples/{filename}.cairo"
    os.system(f"vyro transpile {file_path} --output {expected_cairo_file_path}")

    assert os.path.exists(expected_cairo_file_path) == True
