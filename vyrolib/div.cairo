%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math import assert_not_zero, signed_div_rem


const HALF_RC_BOUND = 2 ** 64

func vyro_div{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) -> (c: felt):
    alloc_locals

    with_attr error_message("Vyrolib: Division by zero"):
        assert_not_zero(b)
    end

    let (c: felt, rem: felt) = signed_div_rem(a, b, HALF_RC_BOUND)
    return (c)
end
