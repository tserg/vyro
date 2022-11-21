from vyper.semantics.types.value.numeric import ValueTypeDefinition


class CairoTypeDefinition(ValueTypeDefinition):
    """Wrapper class"""


class FeltDefinition(CairoTypeDefinition):
    _id = "felt"
    _max_value = 2**251 + 17 * 2**192 + 1


class CairoUint256Definition(CairoTypeDefinition):
    _id = "Uint256"
    _max_value = 2**256 - 1


class CairoMappingDefinition(CairoTypeDefinition):
    def __init__(self, is_constant, is_public, is_immutable, key_types, value_type, is_array=False):
        super().__init__(is_constant=is_constant, is_public=is_public, is_immutable=is_immutable)

        self.key_types = key_types
        self.value_type = value_type
        self.is_array = is_array

    def __repr__(self):
        return str(self.value_type)
