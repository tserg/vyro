%lang starknet

from starkware.cairo.common.bool import FALSE, TRUE
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math_cmp import is_le_felt

func vyro_lt{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(a: felt, b: felt) -> (
    c: felt
) {
    let diff = a - b;

    if (diff == 0) {
        return (FALSE,);
    }

    let res = is_le_felt(a, b);
    return (res,);
}
