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


def vyper_type_to_cairo_type(vy_typ: BaseTypeDefinition) -> CairoTypeDefinition:
    if isinstance(vy_typ, IntegerAbstractType):

        if vy_typ._bits > 251:
            return CairoUint256Definition(
                is_constant=vy_typ.is_constant,
                is_public=vy_typ.is_public,
                is_immutable=vy_typ.is_immutable,
            )

        else:
            return FeltDefinition(
                is_constant=vy_typ.is_constant,
                is_public=vy_typ.is_public,
                is_immutable=vy_typ.is_immutable,
            )

    elif isinstance(vy_typ, FixedAbstractType):
        raise UnsupportedType(f"{vy_typ} is not supported.")

    return FeltDefinition(False, False, False)
