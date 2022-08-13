# @version ^0.3.5

x: public(int128)
y: public(uint256)
z: public(bool)

@external
def __init__(x: int128, y: uint256, z: bool):
    self.x = x
    self.y = y
    self.z = z
