%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import FALSE
from starkware.cairo.common.uint256 import (
    Uint256,
    uint256_check,
    uint256_add,
)

# Adds two integers.
# Reverts if the sum overflows.
func add256{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr} (
    a: Uint256, b: Uint256
) -> (c: Uint256):
    uint256_check(a)
    uint256_check(b)
    let (c: Uint256, is_overflow) = uint256_add(a, b)
    with_attr error_message("SafeUint256: addition overflow"):
        assert is_overflow = FALSE
    end
    return (c)
end
