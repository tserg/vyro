# @version ^0.3.5

@external
@view
def if_only(x: uint256) -> uint256:
    if x == 5:
        return 7
    return 14

@external
@view
def if_else(x: uint256) -> uint256:
    if x == 5:
        return 7
    else:
        return 14


@external
@view
def if_else_2(x: uint256) -> uint256:
    if x > 100:
        y: uint256 = x + 7
        return y
    else:
        y: uint256 = x - 7
        return y
