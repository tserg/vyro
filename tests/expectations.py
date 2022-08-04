EXPECTATIONS = [
    # .vy filename, [
    #    (method_name, [vyper call_args], expected)
    # ]
    ("state_variable", [
        ("foo", [], None),
        ("a", [], 7),
        ("set_a", [100], None),
        ("a", [], 100),
    ]),
]
