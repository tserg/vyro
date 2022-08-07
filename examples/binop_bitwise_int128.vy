# @version ^0.3.4

@external
@view
def and_int128(a: int128, b: int128) -> int128:
    return a & b

@external
@view
def or_int128(a: int128, b: int128) -> int128:
    return a | b

@external
@view
def xor_int128(a: int128, b: int128) -> int128:
    return a ^ b
