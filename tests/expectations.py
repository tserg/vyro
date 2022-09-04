from ape.exceptions import ContractLogicError
from hexbytes import HexBytes

from tests.utils import FALSE, TRUE, signed_int_to_felt, str_to_int

ERC20_INITIAL_SUPPLY = 1_000 * 10**18
ERC20_TRANSFER_AMT = 100 * 10**18

EXPECTATIONS = [
    # .vy filename, [
    #    (
    #       method_name,
    #       ([vyper call_args], vyper expected, vyper caller),
    #       ([cairo call_args], cairo expected, [cairo event names], cairo_caller),
    #    ),
    # ]
    (
        "as_wei_value",
        (("get_gwei", [[17], 17 * 10**9], [[17], 17 * 10**9]),),
    ),
    (
        "assert_int128",
        (
            ("assert_eq", [[5], ContractLogicError()], [[5], ContractLogicError()]),
            ("assert_eq", [[-1], None], [[signed_int_to_felt(-1)], None]),
            (
                "assert_neq",
                [[-1], ContractLogicError()],
                [[signed_int_to_felt(-1)], ContractLogicError()],
            ),
            ("assert_neq", [[5], None], [[5], None]),
            ("assert_ge", [[-1], None], [[signed_int_to_felt(-1)], None]),
            ("assert_ge", [[-(2**8)], None], [[signed_int_to_felt(-(2**8))], None]),
            (
                "assert_ge",
                [[-(2**9)], ContractLogicError()],
                [[signed_int_to_felt(-(2**9))], ContractLogicError()],
            ),
            ("assert_gt", [[-1], None], [[signed_int_to_felt(-1)], None]),
            (
                "assert_gt",
                [[-(2**8)], ContractLogicError()],
                [[signed_int_to_felt(-(2**8))], ContractLogicError()],
            ),
            (
                "assert_gt",
                [[-(2**9)], ContractLogicError()],
                [[signed_int_to_felt(-(2**9))], ContractLogicError()],
            ),
            (
                "assert_le",
                [[-1], ContractLogicError()],
                [[signed_int_to_felt(-1)], ContractLogicError()],
            ),
            ("assert_le", [[-(2**8)], None], [[signed_int_to_felt(-(2**8))], None]),
            ("assert_le", [[-(2**9)], None], [[signed_int_to_felt(-(2**9))], None]),
            (
                "assert_lt",
                [[-1], ContractLogicError()],
                [[signed_int_to_felt(-1)], ContractLogicError()],
            ),
            (
                "assert_lt",
                [[-(2**8)], ContractLogicError()],
                [[signed_int_to_felt(-(2**8))], ContractLogicError()],
            ),
            ("assert_lt", [[-(2**9)], None], [[signed_int_to_felt(-(2**9))], None]),
        ),
    ),
    (
        "assert_uint256",
        (
            ("assert_eq", [[5], ContractLogicError()], [[5], ContractLogicError()]),
            ("assert_eq", [[0], None], [[0], None]),
            ("assert_neq", [[0], ContractLogicError()], [[0], ContractLogicError()]),
            ("assert_neq", [[5], None], [[5], None]),
            ("assert_ge", [[2**200], None], [[2**200], None]),
            ("assert_ge", [[2**144], None], [[2**144], None]),
            ("assert_ge", [[0], ContractLogicError()], [[0], ContractLogicError()]),
            ("assert_gt", [[2**200], None], [[2**200], None]),
            ("assert_gt", [[2**144], ContractLogicError()], [[2**144], ContractLogicError()]),
            ("assert_gt", [[0], ContractLogicError()], [[0], ContractLogicError()]),
            ("assert_le", [[2**200], ContractLogicError()], [[2**200], ContractLogicError()]),
            ("assert_le", [[2**144], None], [[2**144], None]),
            ("assert_le", [[0], None], [[0], None]),
            ("assert_lt", [[2**200], ContractLogicError()], [[2**200], ContractLogicError()]),
            ("assert_lt", [[2**144], ContractLogicError()], [[2**144], ContractLogicError()]),
            ("assert_lt", [[0], None], [[0], None]),
        ),
    ),
    (
        "augassign",
        (
            ("aug_int128", [[5], None], [[5], None]),
            ("a", [[], 5], [[], 5]),
            ("aug_int128_rhs", [[5], 10], [[5], 10]),
            ("aug_uint256", [[5], None], [[5], None]),
            ("aug_uint256_rhs", [[5], 10], [[5], 10]),
            ("b", [[], 5], [[], 5]),
            ("aug_int128_local", [[5], 15], [[5], 15]),
            ("aug_uint256_local", [[5], 15], [[5], 15]),
        ),
    ),
    (
        "binop_arithmetic_int128",
        (
            ("add_int128", [[1, 1], 2], [[1, 1], 2]),
            ("sub_int128", [[2, 1], 1], [[2, 1], 1]),
            ("mul_int128", [[2, 2], 4], [[2, 2], 4]),
            ("div_int128", [[4, 2], 2], [[4, 2], 2]),
            ("mod_int128", [[7, 3], 1], [[7, 3], 1]),
            ("pow_int128", [[3], 2187], [[3], 2187]),
        ),
    ),
    (
        "binop_arithmetic_uint256",
        (
            ("add_uint256", [[1, 1], 2], [[1, 1], 2]),
            ("sub_uint256", [[2, 1], 1], [[2, 1], 1]),
            ("mul_uint256", [[2, 2], 4], [[2, 2], 4]),
            ("div_uint256", [[4, 2], 2], [[4, 2], 2]),
            ("mod_uint256", [[7, 3], 1], [[7, 3], 1]),
            ("pow_uint256", [[18], 10**18], [[18], 10**18]),
        ),
    ),
    (
        "binop_bitwise_int128",
        (
            ("and_int128", [[200, 231], 192], [[200, 231], 192]),
            ("or_int128", [[150, 200], 222], [[150, 200], 222]),
            ("xor_int128", [[150, 200], 94], [[150, 200], 94]),
        ),
    ),
    (
        "binop_bitwise_uint256",
        (
            ("and_uint256", [[200, 231], 192], [[200, 231], 192]),
            ("or_uint256", [[150, 200], 222], [[150, 200], 222]),
            ("xor_uint256", [[150, 200], 94], [[150, 200], 94]),
        ),
    ),
    ("binop_nested_arithmetic_int128", (("add_mul_int128", [[100, 9], 101], [[100, 9], 101]),)),
    (
        "binop_nested_arithmetic_uint256",
        (("pow_mul_uint256", [[100, 18], 100 * 10**18], [[100, 18], 100 * 10**18]),),
    ),
    (
        "boolop",
        (
            ("bool_and", [[True, False], False], [[1, 0], 0]),
            ("bool_and", [[True, True], True], [[1, 1], 1]),
            ("bool_and", [[False, False], False], [[0, 0], 0]),
            ("bool_or", [[True, False], True], [[1, 0], 1]),
            ("bool_or", [[False, True], True], [[0, 1], 1]),
            ("bool_or", [[True, True], True], [[1, 1], 1]),
            ("bool_or", [[False, False], False], [[0, 0], 0]),
        ),
    ),
    (
        "block_number",
        (("get_block_no", [[], None], [[], None]),),
    ),
    (
        "block_timestamp",
        (("get_timestamp", [[], None], [[], None]),),
    ),
    (
        "compare_int128",
        (
            ("compare_eq", [[7, 7], True], [[7, 7], TRUE]),
            ("compare_eq", [[7, 8], False], [[7, 8], FALSE]),
            ("compare_neq", [[7, 8], True], [[7, 8], TRUE]),
            ("compare_neq", [[7, 7], False], [[7, 7], FALSE]),
            ("compare_ge", [[10, 1], True], [[10, 1], TRUE]),
            ("compare_ge", [[1, 1], True], [[1, 1], TRUE]),
            ("compare_ge", [[0, 1], False], [[0, 1], FALSE]),
            ("compare_gt", [[10, 1], True], [[10, 1], TRUE]),
            ("compare_gt", [[1, 1], False], [[1, 1], FALSE]),
            ("compare_gt", [[0, 1], False], [[0, 1], FALSE]),
            ("compare_le", [[10, 1], False], [[10, 1], FALSE]),
            ("compare_le", [[1, 1], True], [[1, 1], TRUE]),
            ("compare_le", [[0, 1], True], [[0, 1], TRUE]),
            ("compare_lt", [[10, 1], False], [[10, 1], FALSE]),
            ("compare_lt", [[1, 1], False], [[1, 1], FALSE]),
            ("compare_lt", [[0, 1], True], [[0, 1], TRUE]),
        ),
    ),
    (
        "compare_uint256",
        (
            ("compare_eq", [[7, 7], True], [[7, 7], TRUE]),
            ("compare_eq", [[7, 8], False], [[7, 8], FALSE]),
            ("compare_neq", [[7, 8], True], [[7, 8], TRUE]),
            ("compare_neq", [[7, 7], False], [[7, 7], FALSE]),
            ("compare_ge", [[10, 1], True], [[10, 1], TRUE]),
            ("compare_ge", [[1, 1], True], [[1, 1], TRUE]),
            ("compare_ge", [[0, 1], False], [[0, 1], FALSE]),
            ("compare_gt", [[10, 1], True], [[10, 1], TRUE]),
            ("compare_gt", [[1, 1], False], [[1, 1], FALSE]),
            ("compare_gt", [[0, 1], False], [[0, 1], FALSE]),
            ("compare_le", [[10, 1], False], [[10, 1], FALSE]),
            ("compare_le", [[1, 1], True], [[1, 1], TRUE]),
            ("compare_le", [[0, 1], True], [[0, 1], TRUE]),
            ("compare_lt", [[10, 1], False], [[10, 1], FALSE]),
            ("compare_lt", [[1, 1], False], [[1, 1], FALSE]),
            ("compare_lt", [[0, 1], True], [[0, 1], TRUE]),
        ),
    ),
    (
        "constants",
        (
            ("add_to_int128", [[101], -1899], [[101], signed_int_to_felt(-1899)]),
            ("add_to_uint8", [[111], 234], [[111], 234]),
            ("add_to_uint256", [[111], 234], [[111], 234]),
            (
                "get_addr",
                [[], "0x3cD751E6b0078Be393132286c442345e5DC49699"],
                [[], 347341241061202630446643950033957413255697962649],
            ),
            ("get_bool", [[], True], [[], 1]),
            (
                "get_bytes20",
                [[], HexBytes("0x3cd751e6b0078be393132286c442345e5dc49699")],
                [[], 347341241061202630446643950033957413255697962649],
            ),
            (
                "get_bytes_array_10",
                [[], b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10"],
                [[], 4759477275222530853136],
            ),
            ("get_string", [[], "transpiler"], [[], str_to_int("transpiler")]),
        ),
    ),
    (
        "constructor",
        (
            ("x", [[], -10], [[], signed_int_to_felt(-10)]),
            ("y", [[], 100], [[], 100]),
            ("z", [[], True], [[], 1]),
        ),
        ([-10, 100, True], [signed_int_to_felt(-10), 100, 1]),
    ),
    (
        "convert",
        (
            ("uint8_to_uint256", [[255], 255], [[255], 255]),
            ("uint8_to_uint128", [[246], 246], [[246], 246]),
            ("uint128_to_uint8", [[255], 255], [[255], 255]),
            (
                "uint128_to_uint8_external",
                [[256], ContractLogicError()],
                [[256], ContractLogicError()],
            ),
        ),
    ),
    (
        "empty",
        (
            ("get_addr", [[], "0x0000000000000000000000000000000000000000"], [[], 0]),
            ("get_uint256", [[], 0], [[], 0]),
        ),
    ),
    (
        "ERC20",
        (
            (
                "balanceOf",
                [["ETH_OWNER"], ERC20_INITIAL_SUPPLY],
                [["STARKNET_OWNER"], ERC20_INITIAL_SUPPLY],
            ),
            (
                "transfer",
                [["ETH_USER", ERC20_TRANSFER_AMT], None],
                [["STARKNET_USER", ERC20_TRANSFER_AMT], None, ["Transfer"]],
            ),
            (
                "balanceOf",
                [["ETH_OWNER"], ERC20_INITIAL_SUPPLY - ERC20_TRANSFER_AMT],
                [["STARKNET_OWNER"], ERC20_INITIAL_SUPPLY - ERC20_TRANSFER_AMT],
            ),
            (
                "balanceOf",
                [["ETH_USER"], ERC20_TRANSFER_AMT],
                [["STARKNET_USER"], ERC20_TRANSFER_AMT],
            ),
            (
                "approve",
                [["ETH_GUEST", ERC20_TRANSFER_AMT], None, "eth_owner"],
                [["STARKNET_GUEST", ERC20_TRANSFER_AMT], None, ["Approval"], "starknet_owner"],
            ),
            (
                "allowance",
                [["ETH_OWNER", "ETH_GUEST"], ERC20_TRANSFER_AMT],
                [["STARKNET_OWNER", "STARKNET_GUEST"], ERC20_TRANSFER_AMT],
            ),
            (
                "transferFrom",
                [["ETH_OWNER", "ETH_USER", ERC20_TRANSFER_AMT], None, "eth_guest"],
                [
                    ["STARKNET_OWNER", "STARKNET_USER", ERC20_TRANSFER_AMT],
                    None,
                    ["Transfer"],
                    "starknet_guest",
                ],
            ),
            (
                "balanceOf",
                [["ETH_OWNER"], ERC20_INITIAL_SUPPLY - ERC20_TRANSFER_AMT * 2],
                [["STARKNET_OWNER"], ERC20_INITIAL_SUPPLY - ERC20_TRANSFER_AMT * 2],
            ),
            (
                "balanceOf",
                [["ETH_USER"], ERC20_TRANSFER_AMT * 2],
                [["STARKNET_USER"], ERC20_TRANSFER_AMT * 2],
            ),
            # Successful mint
            (
                "mint",
                [["ETH_OWNER", ERC20_TRANSFER_AMT * 2], None, "eth_owner"],
                [["STARKNET_OWNER", ERC20_TRANSFER_AMT * 2], None, ["Transfer"], "starknet_owner"],
            ),
            (
                "balanceOf",
                [["ETH_OWNER"], ERC20_INITIAL_SUPPLY],
                [["STARKNET_OWNER"], ERC20_INITIAL_SUPPLY],
            ),
            (
                "totalSupply",
                [[], ERC20_INITIAL_SUPPLY + ERC20_TRANSFER_AMT * 2],
                [[], ERC20_INITIAL_SUPPLY + ERC20_TRANSFER_AMT * 2],
            ),
            # Unauthorised mint
            (
                "mint",
                [["ETH_USER", ERC20_TRANSFER_AMT * 2], ContractLogicError(), "eth_user"],
                [["STARKNET_USER", ERC20_TRANSFER_AMT], ContractLogicError(), [], "starknet_user"],
            ),
            (
                "balanceOf",
                [["ETH_USER"], ERC20_TRANSFER_AMT * 2],
                [["STARKNET_USER"], ERC20_TRANSFER_AMT * 2],
            ),
            (
                "totalSupply",
                [[], ERC20_INITIAL_SUPPLY + ERC20_TRANSFER_AMT * 2],
                [[], ERC20_INITIAL_SUPPLY + ERC20_TRANSFER_AMT * 2],
            ),
        ),
        (
            ["Dogecoin", "DOGE", 18, 1_000, "ETH_OWNER", "ETH_OWNER"],
            [
                str_to_int("Dogecoin"),
                str_to_int("DOGE"),
                18,
                1_000,
                "STARKNET_OWNER",
                "STARKNET_OWNER",
            ],
        ),
    ),
    ("event", [("foo", [[111], None], [[111], None, ["Trigger", "IndexedTrigger"]])]),
    (
        "internal_fns",
        (
            ("get_abc", [[], 0], [[], 0]),
            ("foo", [[77], None], [[77], None]),
            ("get_abc", [[], 154], [[], 154]),
            ("get_xyz", [[], 1], [[], 1]),
            ("baz", [[77], None], [[77], None]),
            ("get_xyz", [[], 155], [[], 155]),
        ),
    ),
    (
        "if",
        (
            ("if_only", [[5], 7], [[5], 7]),
            ("if_only", [[6], 14], [[6], 14]),
            ("if_else", [[5], 7], [[5], 7]),
            ("if_else", [[6], 14], [[6], 14]),
            ("if_else_2", [[101], 108], [[101], 108]),
            ("if_else_2", [[99], 92], [[99], 92]),
        ),
    ),
    (
        "if_nested",
        (
            ("if_only", [[10], 7], [[10], 7]),
            ("if_only", [[15], 14], [[15], 14]),
            ("if_only", [[4], 21], [[4], 21]),
            ("if_else", [[10], 7], [[10], 7]),
            ("if_else", [[15], 14], [[15], 14]),
            ("if_else", [[4], 21], [[4], 21]),
            ("if_else_2", [[101], 108], [[101], 108]),
            ("if_else_2", [[110], 217], [[110], 217]),
            ("if_else_2", [[99], 92], [[99], 92]),
            ("if_else_2", [[89], 81], [[89], 81]),
        ),
    ),
    (
        "immutable",
        (
            ("get_A", [[], -7], [[], signed_int_to_felt(-7)]),
            ("get_B", [[], 12345], [[], 12345]),
            ("get_C", [[], True], [[], 1]),
            ("get_D", [[], "0x0000000000000000000000000000000000012345"], [[], 74565]),
            ("get_E", [[], "vyper"], [[], str_to_int("vyper")]),
        ),
        (
            [-7, 12345, True, "0x0000000000000000000000000000000000012345", "vyper"],
            [signed_int_to_felt(-7), 12345, 1, 74565, str_to_int("vyper")],
        ),
        "minmax",
        (
            ("get_min_uint128", [[1, 2], 1], [[1, 2], 1]),
            ("get_min_uint128", [[1, 1], 1], [[1, 1], 1]),
            ("get_max_uint128", [[1, 2], 2], [[1, 2], 2]),
            ("get_max_uint128", [[1, 1], 1], [[1, 1], 1]),
            ("get_min_uint256", [[1, 2], 1], [[1, 2], 1]),
            ("get_min_uint256", [[1, 1], 1], [[1, 1], 1]),
            ("get_max_uint256", [[1, 2], 2], [[1, 2], 2]),
            ("get_max_uint256", [[1, 1], 1], [[1, 1], 1]),
        ),
    ),
    (
        "msg_sender",
        (
            ("set_msg_sender", [[], None], [[], None]),
            ("a", [[], "ETH_OWNER"], [[], "STARKNET_OWNER"]),  # Dummy value
        ),
    ),
    (
        "msg_sender_duplicate",
        (
            ("set_msg_sender", [[], None], [[], None]),
            ("a", [[], "ETH_OWNER"], [[], "STARKNET_OWNER"]),  # Dummy value
            ("b", [[], "ETH_OWNER"], [[], "STARKNET_OWNER"]),  # Dummy value
        ),
    ),
    (
        "raise",
        (
            ("conditional_raise", [[5], None], [[5], None]),
            ("conditional_raise", [[15], ContractLogicError()], [[15], ContractLogicError()]),
            ("unconditional_raise", [[], ContractLogicError()], [[], ContractLogicError()]),
        ),
    ),
    (
        "state_variable_int128",
        (
            ("set_a", [[-10], None], [[signed_int_to_felt(-10)], None]),
            ("a", [[], -10], [[], signed_int_to_felt(-10)]),
            ("set_b", [[100], None], [[100], None]),
            ("b", [[], 100], [[], 100]),
            ("set_c", [[], None], [[], None]),
            ("c", [[], 90], [[], 90]),
        ),
    ),
    (
        "state_variable_mapping",
        (
            ("b", [[10], 0], [[10], 0]),
            ("set_b", [[10, 77], None], [[10, 77], None]),
            ("b", [[10], 77], [[10], 77]),
        ),
    ),
    (
        "state_variable_nested_mapping",
        (
            ("set_a", [[123, 123, 456], None], [[123, 123, 456], None]),
            ("a", [[123, 123], 456], [[123, 123], 456]),
            ("set_a_augassign", [[123, 123, 44], None], [[123, 123, 44], None]),
            ("a", [[123, 123], 500], [[123, 123], 500]),
            ("set_a", [[123, 246, 1234], None], [[123, 246, 1234], None]),
            ("view_a_assign", [[123, 123], 1234], [[123, 123], 1234]),
        ),
    ),
    (
        "state_variable_uint256",
        (
            ("foo", [[], None], [[], None]),
            ("a", [[], 7], [[], 7]),
            ("set_a", [[100], None], [[100], None]),
            ("a", [[], 100], [[], 100]),
            ("set_a", [[2**256 - 1], None], [[2**256 - 1], None]),
            ("a", [[], 2**256 - 1], [[], 2**256 - 1]),
        ),
    ),
    (
        "unary",
        (
            ("usub_constant", [[], -1], [[], signed_int_to_felt(-1)]),
            ("usub_arg", [[75], -75], [[75], signed_int_to_felt(-75)]),
            (
                "not_uint256",
                [
                    [2**200],
                    115792089237316193816632940749697632311307892324477961517254590225120294338559,
                ],
                [
                    [2**200],
                    115792089237316193816632940749697632311307892324477961517254590225120294338559,
                ],
            ),
        ),
    ),
]
