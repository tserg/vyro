from vyper.semantics.types.value.numeric import ValueTypeDefinition


class CairoTypeDefinition(ValueTypeDefinition):
    """Wrapper class"""


class FeltDefinition(CairoTypeDefinition):
    _id = "felt"
    _max_value = 2**251 + 17 * 2**192 + 1


class CairoUint256Definition(CairoTypeDefinition):
    _id = "Uint256"
    _max_value = 2**256 - 1
