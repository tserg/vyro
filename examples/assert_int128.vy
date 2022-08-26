# @version ^0.3.5

@external
def assert_eq(x: int128):
    assert x == -1, "Error message"

@external
def assert_neq(x: int128):
    assert x != -1, "Error message"

@external
def assert_ge(x: int128):
    assert x >= - 2 ** 8, "Error message"

@external
def assert_gt(x: int128):
    assert x > - 2 ** 8, "Error message"

@external
def assert_le(x: int128):
    assert x <= - 2 ** 8, "Error message"

@external
def assert_lt(x: int128):
    assert x < - 2 ** 8, "Error message"
