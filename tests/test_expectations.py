import os

import ape
import pytest
from ape.api.transactions import ReceiptAPI
from ape.exceptions import ContractLogicError
from ape_starknet.transactions import InvokeFunctionReceipt
from vyper.utils import hex_to_int

from tests.expectations import EXPECTATIONS
from tests.unsupported import UNSUPPORTED
from tests.utils import replace_args, transpile_to_cairo


# Perform tests in vyper
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_vyper_code(request, project, eth_owner, eth_user, eth_guest, code):
    """
    Test Vyper code against expectations.
    """
    filename = code[0]
    contract_object = project.get_contract(filename)

    # Obtain the `ContractInstance`
    if len(code) >= 3:
        constructor_args = code[2][0]
        replace_args(
            constructor_args,
            [
                ("ETH_OWNER", eth_owner.address),
                ("ETH_USER", eth_user.address),
                ("ETH_GUEST", eth_guest.address),
            ],
        )
        contract = eth_owner.deploy(contract_object, *constructor_args)
    else:
        contract = eth_owner.deploy(contract_object)

    print(f"Testing Vyper contract: {filename}.vy")

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        vyper_args = c[1]

        replace_args(
            vyper_args,
            [
                ("ETH_OWNER", eth_owner.address),
                ("ETH_USER", eth_user.address),
                ("ETH_GUEST", eth_guest.address),
            ],
        )

        call_args = vyper_args[0]
        expected = vyper_args[1]

        caller = eth_owner
        if len(vyper_args) >= 3:
            account_name = vyper_args[2]
            caller = request.getfixturevalue(account_name)

        print(f"Testing function: {function_name}")
        fn_call = getattr(contract, function_name)

        if expected is None:
            fn_call(*call_args, sender=caller)

        elif isinstance(expected, ContractLogicError):
            with ape.reverts():
                fn_call(*call_args, sender=caller)

        else:
            ret = fn_call(*call_args, sender=caller)
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
@pytest.mark.usefixtures("starknet_devnet")
@pytest.mark.parametrize("code", EXPECTATIONS)
def test_cairo_code(request, project, starknet_owner, starknet_user, starknet_guest, code):
    """
    Test Cairo code against expectations.
    """
    filename = f"{code[0]}_transpiled"

    contract_object = project.get_contract(filename)

    # Obtain the `ContractInstance`
    if len(code) >= 3:
        constructor_args = code[2][1]
        replace_args(
            constructor_args,
            [
                ("STARKNET_OWNER", starknet_owner.address),
                ("STARKNET_USER", starknet_user.address),
                ("STARKNET_GUEST", starknet_guest.address),
            ],
        )
        contract = contract_object.deploy(*constructor_args)
    else:
        contract = contract_object.deploy()

    print(f"Testing Cairo contract: {filename}.cairo")

    test_cases = code[1]
    for c in test_cases:
        function_name = c[0]
        cairo_args = c[2]

        replace_args(
            cairo_args,
            [
                ("STARKNET_OWNER", hex_to_int(starknet_owner.address)),
                ("STARKNET_USER", hex_to_int(starknet_user.address)),
                ("STARKNET_GUEST", hex_to_int(starknet_guest.address)),
            ],
        )

        call_args = cairo_args[0]
        expected = cairo_args[1]

        caller = starknet_owner
        if len(cairo_args) >= 4:
            account_name = cairo_args[3]
            caller = request.getfixturevalue(account_name)

        print(f"Testing function: {function_name}")
        fn_call = getattr(contract, function_name)

        if expected is None:
            receipt = fn_call(*call_args, sender=caller)

            # Test for events.
            if len(cairo_args) >= 3:
                expected_events = cairo_args[2]
                logs = receipt.decode_logs()

                for log in logs:
                    event_name = log.event_name
                    if event_name in expected_events:
                        expected_events.remove(event_name)

                # Assert all events have been popped off
                assert len(expected_events) == 0

        elif isinstance(expected, ContractLogicError):
            with ape.reverts():
                fn_call(*call_args, sender=caller)

        else:
            ret = fn_call(*call_args)
            assert not isinstance(ret, InvokeFunctionReceipt)
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
