%lang starknet

from starkware.cairo.common.bool import FALSE, TRUE
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.uint256 import Uint256, uint256_le

func vyro_is_zero{range_check_ptr}(a: felt) -> (res: felt) {
    if (a == 0) {
        return (TRUE,);
    }

    return (FALSE,);
}

func vyro_uint256_is_zero{range_check_ptr}(a: Uint256) -> (res: felt) {
    return uint256_le(a, Uint256(low=0, high=0));
}
