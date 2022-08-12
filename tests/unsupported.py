from vyro.exceptions import FeltOverflowException, UnsupportedOperation

UNSUPPORTED = [
    # .vy filename, expected exception
    ("bytes32_constant", FeltOverflowException),
    ("pow_uint256", UnsupportedOperation),
    ("uint256_constant", FeltOverflowException),
    ("unary_not", UnsupportedOperation),
]
