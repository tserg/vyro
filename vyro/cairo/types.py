from vyper.semantics.types.abstract import FixedAbstractType, IntegerAbstractType
from vyper.semantics.types.bases import BaseTypeDefinition
from vyper.semantics.types.value.numeric import ValueTypeDefinition

from vyro.exceptions import UnsupportedType


class CairoTypeDefinition(ValueTypeDefinition):
    """Wrapper class"""


class FeltDefinition(CairoTypeDefinition):
    _id = "felt"
    _max_value = 2**251 + 17 * 2**192 + 1


class CairoUint256Definition(CairoTypeDefinition):
    _id = "Uint256"
    _max_value = 2**256 - 1


def get_cairo_type(typ: BaseTypeDefinition) -> CairoTypeDefinition:
    if isinstance(typ, CairoTypeDefinition):
        return typ

    if isinstance(typ, IntegerAbstractType):

        if typ._bits > 251:
            return CairoUint256Definition(
                is_constant=typ.is_constant,
                is_public=typ.is_public,
                is_immutable=typ.is_immutable,
            )

        else:
            return FeltDefinition(
                is_constant=typ.is_constant,
                is_public=typ.is_public,
                is_immutable=typ.is_immutable,
            )

    elif isinstance(typ, FixedAbstractType):
        raise UnsupportedType(f"{typ} is not supported.")

    return FeltDefinition(False, False, False)
