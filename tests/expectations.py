EXPECTATIONS = [
    # .vy filename, [
    #    (method_name, [vyper call_args], expected)
    # ]
    ("state_variable", [
        ("foo", [], None),
        ("a", [], 7),
        ("set_a", [100], None),
        ("a", [], 100),
        ("set_a", [2 ** 256 - 1], None),
        ("a", [], 2 ** 256 - 1),
    ]),
]
