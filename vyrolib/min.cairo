%lang starknet

from starkware.cairo.common.bool import FALSE, TRUE
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math_cmp import is_le_felt
from starkware.cairo.common.uint256 import Uint256, uint256_le

func vyro_min{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) -> (c: felt) {
    let res = is_le_felt(a, b);

    if (res == TRUE) {
        return (a,);
    }

    return (b,);
}

func min256{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: Uint256, b: Uint256
) -> (c: Uint256) {
    let (res) = uint256_le(a, b);

    if (res == TRUE) {
        return (a,);
    }

    return (b,);
}
