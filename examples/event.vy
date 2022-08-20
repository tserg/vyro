# @version ^0.3.5

event Trigger:
    value: uint256

@external
def foo(x: uint256):
    log Trigger(x)
