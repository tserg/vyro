from vyro.exceptions import FeltOverflowException, UnsupportedOperation

UNSUPPORTED = [
    # .vy filename, expected exception
    ("pow_uint256", UnsupportedOperation),
    ("uint256_constant", FeltOverflowException),
    ("unary_not", UnsupportedOperation),
]
