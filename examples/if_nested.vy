# @version ^0.3.5

@external
@view
def if_only(x: uint256) -> uint256:
    if x > 5:
        y: uint256 = x
        if y == 10:
            return 7
        return 14
    return 21

@external
@view
def if_else(x: int128) -> int128:
    if x > 5:
        y: int128 = x
        if y == 10:
            return 7
        else:
            return 14
    else:
        return 21

@external
@view
def if_else_2(x: uint256) -> uint256:
    if x > 100:
        y: uint256 = x + 7
        if y < 110:
            return y
        else:
            return y + 100
    else:
        y: uint256 = x - 7
        if y > 90:
            return y
        else:
            return y - 1
