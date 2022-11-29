# @version ^0.3.7

a: uint8[3]

@external
def set_a(i: uint8, x: uint8):
    self.a[i] = x

@external
@view
def get_a(i: uint8) -> uint8:
    return self.a[i]

@external
@view
def get_memory_a(i: uint8) -> uint8:
    a: uint8[3] = [32, 64, 128]
    return a[i]

@external
@view
def get_memory_a_assigned(i: uint8) -> uint8:
    a: uint8[3] = [32, 64, 128]
    b: uint8 = a[i]
    return b
