# @version ^0.3.4

@external
@view
def add_mul_int128(a: int128, b: int128) -> int128:
    return a + b % 2
