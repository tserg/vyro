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
