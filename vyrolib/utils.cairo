from starkware.cairo.common.math import split_felt
from starkware.cairo.common.uint256 import Uint256


func felt_to_uint256{range_check_ptr}(x : felt) -> (val : Uint256):
    let (hi: felt, lo: felt) = split_felt(x)
    return (Uint256(low=lo, high=hi))
end

func uint256_to_felt(x : Uint256) -> (val : felt):
    let val = x.low + x.high * 2 ** 128
    return (val)
end
