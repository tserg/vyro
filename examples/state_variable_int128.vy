# @version ^0.3.3

a: public(int128)
b: public(int128)
c: public(int128)

@external
def set_a(x: int128):
    self.a = x

@external
def set_b(x: int128):
    self.b = x

@external
def set_c():
    self.c = self.a + self.b
