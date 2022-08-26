%lang starknet

from starkware.cairo.common.bool import FALSE, TRUE
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math_cmp import is_not_zero
from starkware.cairo.common.uint256 import Uint256, uint256_eq

func vyro_neq{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    a : felt, b : felt
) -> (c : felt):
    let diff = a - b
    let (res) = is_not_zero(diff)
    return (res)
end

func neq256{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    a : Uint256, b : Uint256
) -> (c : felt):
    let (is_eq) = uint256_eq(a, b)

    if is_eq == FALSE:
        return (TRUE)
    end

    return (FALSE)
end
