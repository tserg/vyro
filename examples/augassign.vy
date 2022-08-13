# @version ^0.3.5

a: public(int128)
b: public(uint256)

@external
def aug_int128(x: int128) -> int128:
    self.a += x
    return self.a

@external
@view
def aug_int128_rhs(x: int128) -> int128:
    temp: int128 = x
    temp += self.a
    return temp

@external
def aug_uint256(x: uint256) -> uint256:
    self.b += x
    return self.b

@external
@view
def aug_uint256_rhs(x: uint256) -> uint256:
    temp: uint256 = x
    temp += self.b
    return temp

@external
@view
def aug_int128_local(x: int128) -> int128:
    a: int128 = 10
    a += x
    return a

@external
@view
def aug_uint256_local(x: uint256) -> uint256:
    a: uint256 = 10
    a += x
    return a
