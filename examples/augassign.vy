# @version ^0.3.5

a: public(int128)
b: public(uint256)

@external
def aug_int128(x: int128) -> int128:
    self.a += x
    return self.a

@external
def aug_uint256(x: uint256) -> uint256:
    self.b += x
    return self.b
