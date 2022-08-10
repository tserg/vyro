# @version ^0.3.6

@external
@view
def usub_constant() -> int128:
    a: int128 = -1
    return a

@external
@view
def usub_arg(x: int128) -> int128:
    a: int128 = -x
    return a

@external
@view
def not_uint256(a: uint256) -> uint256:
    return ~a
