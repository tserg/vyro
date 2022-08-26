# @version ^0.3.5

@external
def assert_eq(x: uint256):
    assert x == 0, "Error message"

@external
def assert_neq(x: uint256):
    assert x != 0, "Error message"

@external
def assert_ge(x: uint256):
    assert x >= 2 ** 144, "Error message"

@external
def assert_gt(x: uint256):
    assert x > 2 ** 144, "Error message"

@external
def assert_le(x: uint256):
    assert x <= 2 ** 144, "Error message"

@external
def assert_lt(x: uint256):
    assert x < 2 ** 144, "Error message"
