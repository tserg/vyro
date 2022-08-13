from vyro.exceptions import FeltOverflowException, UnsupportedOperation

UNSUPPORTED = [
    # .vy filename, expected exception
    ("constants/bytes32_constant", FeltOverflowException),
    ("constants/string_constant", FeltOverflowException),
    ("constants/uint256_constant", FeltOverflowException),
    ("pow_uint256", UnsupportedOperation),
    ("unary_not", UnsupportedOperation),
]
