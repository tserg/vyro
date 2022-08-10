from vyro.exceptions import UnsupportedOperation

UNSUPPORTED = [
    # .vy filename, expected exception
    ("pow_uint256", UnsupportedOperation),
    ("unary_not", UnsupportedOperation),
]
