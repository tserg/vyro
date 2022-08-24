%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import TRUE
from starkware.cairo.common.uint256 import Uint256, uint256_check, uint256_mul, uint256_eq

# Multiplies two integers.
# Reverts if product is greater than 2^256.
func mul256{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    a : Uint256, b : Uint256
) -> (c : Uint256):
    alloc_locals
    uint256_check(a)
    uint256_check(b)
    let (a_zero) = uint256_eq(a, Uint256(0, 0))
    if a_zero == TRUE:
        return (a)
    end

    let (b_zero) = uint256_eq(b, Uint256(0, 0))
    if b_zero == TRUE:
        return (b)
    end

    let (c : Uint256, overflow : Uint256) = uint256_mul(a, b)
    with_attr error_message("SafeUint256: multiplication overflow"):
        assert overflow = Uint256(0, 0)
    end
    return (c)
end
