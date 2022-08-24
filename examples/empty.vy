# @version ^0.3.5

ADDR: constant(address) = empty(address)

@external
@view
def get_addr() -> address:
    return ADDR

@external
@view
def get_uint256() -> uint256:
    return empty(uint256)
