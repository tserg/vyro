# @version ^0.3.6

FOO: constant(uint8) = 123

@external
@view
def add_to_constant(x: uint8) -> uint8:
    return x + FOO
