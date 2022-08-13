# @version ^0.3.6

INT128_VALID: constant(int128) = -2000
UINT8_VALID: constant(uint8) = 123
UINT256_VALID: constant(uint256) = 123

ADDR: constant(address) = 0x3cD751E6b0078Be393132286c442345e5DC49699
BOOL: constant(bool) = True
FIXED_BYTES_20: constant(bytes20) = 0x3cd751e6b0078be393132286c442345e5dc49699
STRING_10: constant(String[10]) = "transpiler"

@external
@view
def add_to_int128(x: int128) -> int128:
    return x + INT128_VALID

@external
@view
def add_to_uint8(x: uint8) -> uint8:
    return x + UINT8_VALID

@external
@view
def add_to_uint256(x: uint256) -> uint256:
    return x + UINT256_VALID

@external
@view
def get_addr() -> address:
    return ADDR

@external
@view
def get_bool() -> bool:
    return BOOL

@external
@view
def get_bytes20() -> bytes20:
    return FIXED_BYTES_20

@external
@view
def get_string() -> String[10]:
    return STRING_10
