# @version ^0.3.5

@external
@view
def address_to_uint256(x: address) -> uint256:
    return convert(x, uint256)
