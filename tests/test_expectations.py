import os

import ape
import pytest
from ape.api.transactions import ReceiptAPI
from ape.exceptions import ContractLogicError
from ape_starknet.transactions import InvocationReceipt
from vyper.utils import hex_to_int

from tests.expectations import EXPECTATIONS
from tests.unsupported import UNSUPPORTED
from tests.utils import replace_args, transpile_to_cairo


# Perform tests in vyper
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_vyper_code(project, eth_owner, eth_user, code):
    """
    Test Vyper code against expectations.
    """
    filename = code[0]
    contract_object = project.get_contract(filename)

    # Obtain the `ContractInstance`
    if len(code) == 2:
        contract = eth_owner.deploy(contract_object)
    elif len(code) == 3:
        constructor_args = code[2][0]
        replace_args(
            constructor_args,
            [("ETH_OWNER", eth_owner.address), ("ETH_USER", eth_user.address)],
        )
        contract = eth_owner.deploy(contract_object, *constructor_args)

    print(f"Testing Vyper contract: {filename}.vy")

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        call_args = c[1]
        replace_args(
            call_args,
            [("ETH_OWNER", eth_owner.address), ("ETH_USER", eth_user.address)],
        )

        expected = c[2]

        if expected == "ETH_USER":
            expected = eth_user.address

        print(f"Testing function: {function_name}")
        fn_call = getattr(contract, function_name)

        if expected is None:
            fn_call(*call_args, sender=eth_user)

        elif isinstance(expected, ContractLogicError):
            with ape.reverts():
                fn_call(*call_args, sender=eth_user)

        else:
            ret = fn_call(*call_args, sender=eth_user)
            assert not isinstance(ret, ReceiptAPI)
            assert ret == expected


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

    print(f"Transpiled Vyper contract: {filename}.vy")

    assert os.path.exists(expected_cairo_file_path) is True


# Perform tests in cairo
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_cairo_code(project, starknet_devnet, starknet_owner, starknet_user, code):
    """
    Test Cairo code against expectations.
    """
    filename = f"{code[0]}_transpiled"

    contract_object = project.get_contract(filename)

    # Obtain the `ContractInstance`
    if len(code) == 2:
        contract = contract_object.deploy()
    elif len(code) == 3:
        constructor_args = code[2][1]
        replace_args(
            constructor_args,
            [
                ("STARKNET_OWNER", starknet_owner.address),
                ("STARKNET_USER", starknet_user.address),
            ],
        )
        contract = contract_object.deploy(*constructor_args)

    print(f"Testing Cairo contract: {filename}.cairo")

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        call_args = c[3]
        replace_args(
            call_args,
            [
                ("STARKNET_OWNER", starknet_owner.address),
                ("STARKNET_USER", starknet_user.address),
            ],
        )

        expected = c[4]

        if expected == "STARKNET_USER":
            expected = hex_to_int(starknet_user.address)

        print(f"Testing function: {function_name}")
        fn_call = getattr(contract, function_name)

        if expected is None:
            receipt = fn_call(*call_args, sender=starknet_user)

            # Test for events.
            if len(c) == 6:
                expected_events = c[5]
                logs = receipt.decode_logs()

                for log in logs:
                    event_name = log.event_name
                    if event_name in expected_events:
                        expected_events.remove(event_name)

                # Assert all events have been popped off
                assert len(expected_events) == 0

        elif isinstance(expected, ContractLogicError):
            with ape.reverts():
                fn_call(*call_args, sender=starknet_user)

        else:
            ret = fn_call(*call_args)
            assert not isinstance(ret, InvocationReceipt)
            assert ret == expected


@pytest.mark.parametrize("code", UNSUPPORTED)
def test_transpile_fail(code, assert_transpile_failed):
    """
    Test failed transpilations of Vyper contracts.
    """
    filename = code[0]
    file_path = f"unsupported/{filename}.vy"
    print(f"Transpiling unsupported Vyper contract: {filename}.vy")

    expected = code[1]

    expected_cairo_file_path = f"examples/{filename}_transpiled.cairo"
    assert_transpile_failed(
        lambda: transpile_to_cairo(file_path, expected_cairo_file_path), expected
    )
