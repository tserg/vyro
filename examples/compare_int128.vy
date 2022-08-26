# @version ^0.3.5

@external
@view
def compare_eq(x: int128, y: int128) -> bool:
    return x == y

@external
@view
def compare_neq(x: int128, y: int128) -> bool:
    z: bool = x != y
    return z

@external
@view
def compare_ge(x: int128, y: int128) -> bool:
    return x >= y

@external
@view
def compare_gt(x: int128, y: int128) -> bool:
    return x > y

@external
@view
def compare_le(x: int128, y: int128) -> bool:
    return x <= y

@external
@view
def compare_lt(x: int128, y: int128) -> bool:
    return x < y
