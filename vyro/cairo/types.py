from vyper.semantics.types.abstract import IntegerAbstractType
from vyper.semantics.types.bases import BaseTypeDefinition
from vyper.semantics.types.value.numeric import ValueTypeDefinition


class CairoTypeDefinition(ValueTypeDefinition):
    """Wrapper class"""


class FeltDefinition(CairoTypeDefinition):
    _id = "felt"
    _max_value = 2**251 + 17 * 2**192 + 1


def vyper_type_to_cairo_type(vy_typ: BaseTypeDefinition) -> CairoTypeDefinition:
    if isinstance(vy_typ, IntegerAbstractType):
        return FeltDefinition(
            is_constant=vy_typ.is_constant,
            is_public=vy_typ.is_public,
            is_immutable=vy_typ.is_immutable,
        )
    return FeltDefinition(False, False, False)
