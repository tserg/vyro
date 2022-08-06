EXPECTATIONS = [
    # .vy filename, [
    #    (method_name, [vyper call_args], vyper expected)
    # ]
    (
        "state_variable",
        [
            ("foo", [], None),
            ("a", [], 7),
            ("set_a", [100], None),
            ("a", [], 100),
            ("set_a", [2**256 - 1], None),
            ("a", [], 2**256 - 1),
        ],
    ),
    (
        "binop_arithmetic_int128",
        [
            ("add_int128", [1, 1], 2),
            ("sub_int128", [2, 1], 1),
            ("mul_int128", [2, 2], 4),
            ("div_int128", [4, 2], 2),
            ("mod_int128", [7, 3], 1),
            ("pow_int128", [3], 2187),
        ],
    ),
    (
        "binop_arithmetic_uint256",
        [
            ("add_uint256", [1, 1], 2),
            ("sub_uint256", [2, 1], 1),
            ("mul_uint256", [2, 2], 4),
            ("div_uint256", [4, 2], 2),
            ("mod_uint256", [7, 3], 1),
        ],
    ),
]
