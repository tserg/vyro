%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import FALSE
from starkware.cairo.common.math import assert_not_zero, signed_div_rem
from starkware.cairo.common.uint256 import (
    Uint256,
    uint256_check,
    uint256_unsigned_div_rem,
    uint256_eq,
)

const HALF_RC_BOUND = 2 ** 64

func vyro_mod{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) -> (c: felt):
    alloc_locals

    with_attr error_message("Vyrolib: Modulo by zero"):
        assert_not_zero(b)
    end

    let (c: felt, rem: felt) = signed_div_rem(a, b, HALF_RC_BOUND)
    return (rem)
end


# Integer division of two numbers. Returns uint256 quotient and remainder.
# Reverts if divisor is zero as per OpenZeppelin's Solidity implementation.
# Cairo's `uint256_unsigned_div_rem` already checks:
#    remainder < divisor
#    quotient * divisor + remainder == dividend
func vyro_mod256{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: Uint256, b: Uint256
) -> (c: Uint256):
    alloc_locals
    uint256_check(a)
    uint256_check(b)

    let (is_zero) = uint256_eq(b, Uint256(0, 0))
    with_attr error_message("Vyrolib: Division by zero"):
        assert is_zero = FALSE
    end

    let (c: Uint256, rem: Uint256) = uint256_unsigned_div_rem(a, b)
    return (rem)
end
