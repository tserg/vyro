%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import FALSE
from starkware.cairo.common.uint256 import (
    Uint256,
    uint256_check,
    uint256_unsigned_div_rem,
    uint256_eq,
)

// Integer division of two numbers. Returns uint256 quotient and remainder.
// Reverts if divisor is zero as per OpenZeppelin's Solidity implementation.
// Cairo's `uint256_unsigned_div_rem` already checks:
//    remainder < divisor
//    quotient * divisor + remainder == dividend
func div256{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: Uint256, b: Uint256
) -> (c: Uint256) {
    alloc_locals;
    uint256_check(a);
    uint256_check(b);

    let (is_zero) = uint256_eq(b, Uint256(0, 0));
    with_attr error_message("SafeUint256: divisor cannot be zero") {
        assert is_zero = FALSE;
    }

    let (c: Uint256, rem: Uint256) = uint256_unsigned_div_rem(a, b);
    return (c,);
}
