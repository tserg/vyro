# @version ^0.3.7

struct Foo:
    a: uint256
    b: int8
    c: bool
    d: address


foo: Foo


@external
def __init__():
    self.foo = Foo({
        a: 777,
        b: -8,
        c: True,
        d: 0xDAFEA492D9c6733ae3d56b7Ed1ADB60692c98Bc5,
    })


@external
@view
def get_storage_struct() -> Foo:
    return self.foo


@external
@view
def get_memory_struct() -> Foo:
    f: Foo = Foo({
        a: 777,
        b: -8,
        c: True,
        d: 0xDAFEA492D9c6733ae3d56b7Ed1ADB60692c98Bc5,
    })
    return f


@external
@view
def get_struct_number(x: uint256) -> uint256:
    res: uint256 = x + self.foo.a
    return res
