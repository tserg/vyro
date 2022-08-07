# @version ^0.3.4

@external
@view
def and_uint256(a: uint256, b: uint256) -> uint256:
    return a & b

@external
@view
def or_uint256(a: uint256, b: uint256) -> uint256:
    return a | b

@external
@view
def xor_uint256(a: uint256, b: uint256) -> uint256:
    return a ^ b
