from hexbytes import HexBytes

from tests.utils import signed_int_to_felt, str_to_int


EXPECTATIONS = [
    # .vy filename, [
    #    (method_name, [vyper call_args], vyper expected, [cairo call_args], cairo expected)
    # ]
    (
        "augassign",
        [
            ("aug_int128", [5], None, [5], None),
            ("a", [], 5, [], 5),
            ("aug_uint256", [5], None, [5], None),
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
            ("get_addr", [], "0x3cD751E6b0078Be393132286c442345e5DC49699", [], 347341241061202630446643950033957413255697962649),
            ("get_bool", [], True, [], 1),
            ("get_bytes20", [], HexBytes("0x3cd751e6b0078be393132286c442345e5dc49699"), [], 347341241061202630446643950033957413255697962649),
            ("get_bytes_array_10", [], b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10", [], 4759477275222530853136),
            ("get_string", [], "transpiler", [], str_to_int("transpiler")),
        ),
    ),
    (
        "state_variable",
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
