# @version ^0.3.5

@external
@view
def get_gwei(x: uint256) -> uint256:
    return as_wei_value(x, "gwei")
