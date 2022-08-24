# @version ^0.3.5

@external
@view
def uint8_to_uint256(x: uint8) -> uint256:
    return convert(x, uint256)

@external
@view
def uint8_to_uint128(x: uint8) -> uint128:
    return convert(x, uint128)

@external
@view
def uint128_to_uint8(x: uint128) -> uint8:
    return convert(x, uint8)

@external
def uint128_to_uint8_external(x: uint128) -> uint8:
    return convert(x, uint8)
