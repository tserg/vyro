# @version ^0.3.3

a: public(uint256)


@external
def foo():
    self.a = 7

@external
def set_a(x: uint256):
    self.a = x
