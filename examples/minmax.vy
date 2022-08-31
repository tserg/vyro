# @version ^0.3.5

@external
@view
def get_min_uint128(a: uint128, b: uint128) -> uint128:
    return min(a, b)

@external
@view
def get_max_uint128(a: uint128, b: uint128) -> uint128:
    return max(a, b)

@external
@view
def get_min_uint256(a: uint256, b: uint256) -> uint256:
    c: uint256 = min(a, b)
    return c

@external
@view
def get_max_uint256(a: uint256, b: uint256) -> uint256:
    c: uint256 = max(a, b)
    return c
