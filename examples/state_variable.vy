# @version ^0.3.3

a: public(uint256)
b: public(HashMap[uint256, uint256])


@external
def foo():
    self.a = 7

@external
def set_a(x: uint256):
    self.a = x

@external
def set_b(a: uint256, b: uint256):
    self.b[a] = b
