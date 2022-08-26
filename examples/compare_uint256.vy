# @version ^0.3.5

@external
@view
def compare_eq(x: uint256, y: uint256) -> bool:
    return x == y

@external
@view
def compare_neq(x: uint256, y: uint256) -> bool:
    z: bool = x != y
    return z

@external
@view
def compare_ge(x: uint256, y: uint256) -> bool:
    return x >= y

@external
@view
def compare_gt(x: uint256, y: uint256) -> bool:
    return x > y

@external
@view
def compare_le(x: uint256, y: uint256) -> bool:
    return x <= y

@external
@view
def compare_lt(x: uint256, y: uint256) -> bool:
    return x < y
