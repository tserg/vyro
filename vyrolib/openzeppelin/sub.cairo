%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import TRUE
from starkware.cairo.common.uint256 import Uint256, uint256_check, uint256_sub, uint256_le

# Subtracts two integers.
# Reverts if minuend (`b`) is greater than subtrahend (`a`).
func sub256{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    a : Uint256, b : Uint256
) -> (c : Uint256):
    alloc_locals
    uint256_check(a)
    uint256_check(b)
    let (is_le) = uint256_le(b, a)
    with_attr error_message("SafeUint256: subtraction overflow"):
        assert is_le = TRUE
    end
    let (c : Uint256) = uint256_sub(a, b)
    return (c)
end
