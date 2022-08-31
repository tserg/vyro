# @version ^0.3.5

A: immutable(int128)
B: immutable(uint256)
C: immutable(bool)
D: immutable(address)
E: immutable(String[5])


@external
def __init__(a: int128, b: uint256, c: bool, d: address, e: String[5]):
    A = a
    B = b
    C = c
    D = d
    E = e


@external
@view
def get_A() -> int128:
    return A

@external
@view
def get_B() -> uint256:
    return B

@external
@view
def get_C() -> bool:
    return C

@external
@view
def get_D() -> address:
    return D

@external
@view
def get_E() -> String[5]:
    return E
