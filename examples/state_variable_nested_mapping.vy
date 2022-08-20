# @version ^0.3.3

a: public(HashMap[uint256, HashMap[uint256, uint256]])

@external
def set_a(x: uint256, y: uint256, z: uint256):
    self.a[x][y] = z

@external
def set_a_augassign(x: uint256, y: uint256, z: uint256):
    self.a[x][y] += z

@external
@view
def view_a_assign(x: uint256, y: uint256) -> uint256:
    z: uint256 = x + y
    i: uint256 = self.a[x][z]
    return i
