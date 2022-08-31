from vyro.exceptions import (
    FeltOverflowException,
    UnsupportedFeature,
    UnsupportedOperation,
    UnsupportedType,
)

UNSUPPORTED = [
    # .vy filename, expected exception
    ("constants/bytes32_constant", FeltOverflowException),
    ("constants/bytesarray32_constant", FeltOverflowException),
    ("constants/string_constant", FeltOverflowException),
    ("constants/uint256_constant", FeltOverflowException),
    ("array", UnsupportedType),
    ("compare_membership", UnsupportedOperation),
    ("convert", UnsupportedFeature),
    ("decimal", UnsupportedType),
    ("dynarray", UnsupportedType),
    ("unary_not", UnsupportedOperation),
]
