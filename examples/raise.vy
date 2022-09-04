# @version ^0.3.5

@external
def conditional_raise(x: uint256):
    if x > 10:
        raise

@external
def unconditional_raise():
    raise
