from typing import List

from vyper import ast as vy_ast
from vyper.semantics.types.abstract import FixedAbstractType, IntegerAbstractType
from vyper.semantics.types.bases import BaseTypeDefinition

from vyro.cairo.types import CairoTypeDefinition, CairoUint256Definition, FeltDefinition
from vyro.exceptions import UnsupportedType


def generate_name_node(node_id: int) -> vy_ast.Name:
    ret = vy_ast.Name(id=f"VYRO_VAR_{node_id}", node_id=node_id, ast_type="Name")
    return ret


def set_parent(child: vy_ast.VyperNode, parent: vy_ast.VyperNode):
    """
    Replica of `set_parent` in `vyper/ast/nodes.py`
    """
    child._parent = parent
    child._depth = getattr(parent, "_depth", -1) + 1


def insert_statement_before(
    node: vy_ast.VyperNode, before: vy_ast.VyperNode, body_node: List[vy_ast.VyperNode]
):
    """
    Helper function to insert a new node before a given node in a list.

    Arguments
    ---------
    node : vy_ast.VyperNode
        Node to insert.
    before : vy_ast.VyperNode
        Node to insert before.
    body: List[vy_ast.VyperNode]
        List of a vy_ast.VyperNode that contains `before` and which `node` is to be added to.
    """
    assert hasattr(body_node, "body")
    body = body_node.body
    node_idx = body.index(before)
    body.insert(node_idx, node)
    set_parent(node, body_node)


def convert_node_type_definition(node: vy_ast.VyperNode) -> CairoTypeDefinition:
    """
    Helper function to update the type of a AST node to its Cairo type.

    Arguments
    ---------
    node : vy_ast.VyperNode
        Node to replace type for.
    """
    assert "type" in node._metadata
    vy_typ = node._metadata["type"]
    cairo_typ = get_cairo_type(vy_typ)
    node._metadata["type"] = cairo_typ
    return cairo_typ


def get_cairo_type(typ: BaseTypeDefinition) -> CairoTypeDefinition:
    """
    Convert a type definition to its Cairo type.
    If the type definition is already a `CairoTypeDefinition`, return.
    """
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
