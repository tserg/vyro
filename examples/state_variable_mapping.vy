# @version ^0.3.3

b: public(HashMap[uint256, uint256])

@external
def set_b(a: uint256, b: uint256):
    self.b[a] = b
