# @version ^0.3.5

abc: uint8
xyz: uint256

@external
def foo(x: uint8):
    self._foo(x)

@internal
def _foo(x: uint8):
    self.abc = x * 2

@external
@view
def get_abc() -> uint8:
    return self.abc

@external
def baz(x: uint256):
    self._baz(x)

@internal
def _baz(x: uint256):
    self.xyz = x * 2

@external
@view
def get_xyz() -> uint256:
    a: uint256 = self.xyz + 1
    return a
