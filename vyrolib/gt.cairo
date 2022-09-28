%lang starknet

from starkware.cairo.common.bool import FALSE, TRUE
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math_cmp import is_le_felt
from starkware.cairo.common.uint256 import Uint256, uint256_le

func vyro_gt{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(a: felt, b: felt) -> (
    c: felt
) {
    let res = is_le_felt(a, b);

    if (res == FALSE) {
        return (TRUE,);
    }

    return (FALSE,);
}

func gt256{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: Uint256, b: Uint256
) -> (c: felt) {
    let (is_le) = uint256_le(a, b);

    if (is_le == FALSE) {
        return (TRUE,);
    }

    return (FALSE,);
}
