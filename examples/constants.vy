# @version ^0.3.6

FOO: constant(uint8) = 123
ADDR: constant(address) = 0x3cD751E6b0078Be393132286c442345e5DC49699

@external
@view
def add_to_constant(x: uint8) -> uint8:
    return x + FOO


@external
@view
def get_addr() -> address:
    return ADDR
