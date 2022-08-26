%lang starknet

from starkware.cairo.common.bool import FALSE, TRUE
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.math_cmp import is_not_zero

func vyro_eq{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
    a : felt, b : felt
) -> (c : felt):
    let diff = a - b
    let (res) = is_not_zero(diff)

    if res == FALSE:
        return (TRUE)
    end

    return (FALSE)
end
