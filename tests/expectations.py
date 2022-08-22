from hexbytes import HexBytes

from ape.exceptions import ContractLogicError

from tests.utils import signed_int_to_felt, str_to_int

EXPECTATIONS = [
    # .vy filename, [
    #    (method_name, [vyper call_args], vyper expected, [cairo call_args], cairo expected, [cairo event names])
    # ]
    (
        "augassign",
        [
            ("aug_int128", [5], None, [5], None),
            ("a", [], 5, [], 5),
            ("aug_int128_rhs", [5], 10, [5], 10),
            ("aug_uint256", [5], None, [5], None),
            ("aug_uint256_rhs", [5], 10, [5], 10),
            ("b", [], 5, [], 5),
            ("aug_int128_local", [5], 15, [5], 15),
            ("aug_uint256_local", [5], 15, [5], 15),
        ],
    ),
    (
        "binop_arithmetic_int128",
        [
            ("add_int128", [1, 1], 2, [1, 1], 2),
            ("sub_int128", [2, 1], 1, [2, 1], 1),
            ("mul_int128", [2, 2], 4, [2, 2], 4),
            ("div_int128", [4, 2], 2, [4, 2], 2),
            ("mod_int128", [7, 3], 1, [7, 3], 1),
            ("pow_int128", [3], 2187, [3], 2187),
        ],
    ),
    (
        "binop_arithmetic_uint256",
        [
            ("add_uint256", [1, 1], 2, [1, 1], 2),
            ("sub_uint256", [2, 1], 1, [2, 1], 1),
            ("mul_uint256", [2, 2], 4, [2, 2], 4),
            ("div_uint256", [4, 2], 2, [4, 2], 2),
            ("mod_uint256", [7, 3], 1, [7, 3], 1),
        ],
    ),
    (
        "binop_bitwise_int128",
        [
            ("and_int128", [200, 231], 192, [200, 231], 192),
            ("or_int128", [150, 200], 222, [150, 200], 222),
            ("xor_int128", [150, 200], 94, [150, 200], 94),
        ],
    ),
    (
        "binop_bitwise_uint256",
        [
            ("and_uint256", [200, 231], 192, [200, 231], 192),
            ("or_uint256", [150, 200], 222, [150, 200], 222),
            ("xor_uint256", [150, 200], 94, [150, 200], 94),
        ],
    ),
    (
        "boolop",
        (
            ("bool_and", [True, False], False, [1, 0], 0),
            ("bool_and", [True, True], True, [1, 1], 1),
            ("bool_and", [False, False], False, [0, 0], 0),
            ("bool_or", [True, False], True, [1, 0], 1),
            ("bool_or", [False, True], True, [0, 1], 1),
            ("bool_or", [True, True], True, [1, 1], 1),
            ("bool_or", [False, False], False, [0, 0], 0),
        ),
    ),
    (
        "constants",
        (
            ("add_to_int128", [101], -1899, [101], signed_int_to_felt(-1899)),
            ("add_to_uint8", [111], 234, [111], 234),
            ("add_to_uint256", [111], 234, [111], 234),
            (
                "get_addr",
                [],
                "0x3cD751E6b0078Be393132286c442345e5DC49699",
                [],
                347341241061202630446643950033957413255697962649,
            ),
            ("get_bool", [], True, [], 1),
            (
                "get_bytes20",
                [],
                HexBytes("0x3cd751e6b0078be393132286c442345e5dc49699"),
                [],
                347341241061202630446643950033957413255697962649,
            ),
            (
                "get_bytes_array_10",
                [],
                b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10",
                [],
                4759477275222530853136,
            ),
            ("get_string", [], "transpiler", [], str_to_int("transpiler")),
        ),
    ),
    (
        "constructor",
        (
            ("x", [], -10, [], signed_int_to_felt(-10)),
            ("y", [], 100, [], 100),
            ("z", [], True, [], 1),
        ),
        ([-10, 100, True], [signed_int_to_felt(-10), 100, 1]),
    ),
    (
        "convert",
        [
            ("uint8_to_uint256", [255], 255, [255], 255),
            ("uint8_to_uint128", [246], 246, [246], 246),
            ("uint128_to_uint8", [255], 255, [255], 255),
            (
                "uint128_to_uint8_external",
                [256],
                ContractLogicError(),
                [256],
                ContractLogicError(),
            ),
        ],
    ),
    (
        "empty",
        [
            ("get_addr", [], "0x0000000000000000000000000000000000000000", [], 0),
            ("get_uint256", [], 0, [], 0),
        ],
    ),
    ("event", [("foo", [111], None, [111], None, ["Trigger", "IndexedTrigger"])]),
    (
        "internal_fns",
        [
            ("get_abc", [], 0, [], 0),
            ("foo", [77], None, [77], None),
            ("get_abc", [], 154, [], 154),
            ("get_xyz", [], 1, [], 1),
            ("baz", [77], None, [77], None),
            ("get_xyz", [], 155, [], 155),
        ],
    ),
    (
        "msg_sender",
        [
            ("set_msg_sender", [], None, [], None),
            ("a", [], "MSG_SENDER", [], "MSG_SENDER"),  # Dummy value
        ],
    ),
    (
        "msg_sender_duplicate",
        [
            ("set_msg_sender", [], None, [], None),
            ("a", [], "MSG_SENDER", [], "MSG_SENDER"),  # Dummy value
            ("b", [], "MSG_SENDER", [], "MSG_SENDER"),  # Dummy value
        ],
    ),
    (
        "state_variable_int128",
        [
            ("set_a", [-10], None, [signed_int_to_felt(-10)], None),
            ("a", [], -10, [], signed_int_to_felt(-10)),
            ("set_b", [100], None, [100], None),
            ("b", [], 100, [], 100),
            ("set_c", [], None, [], None),
            ("c", [], 90, [], 90),
        ],
    ),
    (
        "state_variable_mapping",
        [
            ("b", [10], 0, [10], 0),
            ("set_b", [10, 77], None, [10, 77], None),
            ("b", [10], 77, [10], 77),
        ],
    ),
    (
        "state_variable_nested_mapping",
        [
            ("set_a", [123, 123, 456], None, [123, 123, 456], None),
            ("a", [123, 123], 456, [123, 123], 456),
            ("set_a_augassign", [123, 123, 44], None, [123, 123, 44], None),
            ("a", [123, 123], 500, [123, 123], 500),
            ("set_a", [123, 246, 1234], None, [123, 246, 1234], None),
            ("view_a_assign", [123, 123], 1234, [123, 123], 1234),
        ],
    ),
    (
        "state_variable_uint256",
        [
            ("foo", [], None, [], None),
            ("a", [], 7, [], 7),
            ("set_a", [100], None, [100], None),
            ("a", [], 100, [], 100),
            ("set_a", [2**256 - 1], None, [2**256 - 1], None),
            ("a", [], 2**256 - 1, [], 2**256 - 1),
        ],
    ),
    (
        "unary",
        [
            ("usub_constant", [], -1, [], signed_int_to_felt(-1)),
            ("usub_arg", [75], -75, [75], signed_int_to_felt(-75)),
            (
                "not_uint256",
                [2**200],
                115792089237316193816632940749697632311307892324477961517254590225120294338559,
                [2**200],
                115792089237316193816632940749697632311307892324477961517254590225120294338559,
            ),
        ],
    ),
]
