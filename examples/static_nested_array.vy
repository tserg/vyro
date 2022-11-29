# @version ^0.3.7

a: uint8[3][3]

@external
def set_a(i: uint8, j: uint8, x: uint8):
    self.a[i][j] = x

@external
@view
def get_a(i: uint8, j: uint8) -> uint8:
    return self.a[i][j]

@external
@view
def get_memory_a(i: uint8, j: uint8) -> uint8:
    a: uint8[3][3] = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    return a[i][j]

@external
@view
def get_memory_a_assigned(i: uint8, j: uint8) -> uint8:
    a: uint8[3][3] = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    b: uint8 = a[2][2]
    return b
