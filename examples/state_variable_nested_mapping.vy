# @version ^0.3.3

a: public(HashMap[uint256, HashMap[uint256, uint256]])

@external
def set_a(a: uint256, b: uint256, c: uint256):
    self.a[a][b] = c
