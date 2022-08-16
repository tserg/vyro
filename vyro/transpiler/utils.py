from string import ascii_lowercase as alc
from typing import List

from vyper import ast as vy_ast
from vyper.semantics.types import AddressDefinition
from vyper.semantics.types.abstract import FixedAbstractType, IntegerAbstractType
from vyper.semantics.types.bases import BaseTypeDefinition
from vyper.semantics.types.indexable.mapping import MappingDefinition
from vyper.semantics.types.indexable.sequence import ArrayDefinition, DynamicArrayDefinition

from vyro.cairo.types import (
    CairoMappingDefinition,
    CairoTypeDefinition,
    CairoUint256Definition,
    FeltDefinition,
)
from vyro.exceptions import TranspilerPanic, UnsupportedType
from vyro.transpiler.context import ASTContext


def generate_name_node(node_id: int, name: str = None) -> vy_ast.Name:
    if name is None:
        name = f"VYRO_VAR_{node_id}"
    ret = vy_ast.Name(id=name, node_id=node_id, ast_type="Name")
    return ret


def set_parent(child: vy_ast.VyperNode, parent: vy_ast.VyperNode):
    """
    Replica of `set_parent` in `vyper/ast/nodes.py`
    """
    child._parent = parent
    child._depth = getattr(parent, "_depth", -1) + 1


def insert_statement_before(
    node: vy_ast.VyperNode, before: vy_ast.VyperNode, body_node: vy_ast.VyperNode
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
    if typ is None:
        raise TranspilerPanic("No type provided for conversion")

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

    elif isinstance(typ, (FixedAbstractType, ArrayDefinition, DynamicArrayDefinition)):
        raise UnsupportedType(f"`{type(typ)}` type is not supported.")

    elif isinstance(typ, AddressDefinition):
        return FeltDefinition(
            is_constant=typ.is_constant,
            is_public=typ.is_public,
            is_immutable=typ.is_immutable,
        )

    elif isinstance(typ, MappingDefinition):
        key_types, value_type = get_hashmap_types(typ)
        # Ensure key types and value type are converted
        key_types = list(map(get_cairo_type, key_types))
        value_type = get_cairo_type(value_type)
        return CairoMappingDefinition(
            typ.is_constant, typ.is_public, typ.is_immutable, key_types, value_type
        )

    return FeltDefinition(typ.is_constant, typ.is_public, typ.is_immutable)


def add_implicit_to_function(node: vy_ast.VyperNode, implicit: str):
    """
    Add an implicit argument to parent function node.
    """
    fn_node = node.get_ancestor(vy_ast.FunctionDef)
    fn_node._metadata["implicits"].add(implicit)


def initialise_function_implicits(node: vy_ast.FunctionDef):
    """
    Initialise the implicits attribute in metadata for a FunctionDef node.
    """
    node._metadata["implicits"] = set(
        {"syscall_ptr", "pedersen_ptr", "range_check_ptr"}
    )


def wrap_operation_in_call(
    ast: vy_ast.Module,
    context: ASTContext,
    call_id: str,
    args: List[vy_ast.VyperNode] = [],
    keywords: List[vy_ast.keyword] = [],
) -> vy_ast.Call:
    wrapped_op = vy_ast.Call(
        node_id=context.reserve_id(),
        func=vy_ast.Name(node_id=context.reserve_id(), id=call_id, ast_type="Name"),
        args=args,
        keywords=keywords,
    )
    for a in args:
        set_parent(a, wrapped_op)
        wrapped_op._children.add(a)
    return wrapped_op


def get_hashmap_types(
    typ: BaseTypeDefinition, keys: List[BaseTypeDefinition] = None
) -> (List[BaseTypeDefinition], BaseTypeDefinition):
    if not isinstance(typ, MappingDefinition):
        return keys

    cairo_typ = get_cairo_type(typ.key_type)

    if keys is None:
        keys = []
    keys.append(cairo_typ)

    value_typ = typ.value_type
    if isinstance(value_typ, MappingDefinition):
        return get_hashmap_types(value_typ, keys)

    return keys, value_typ


def extract_mapping_args(
    typ: CairoMappingDefinition, context: ASTContext, include_type: bool = False
):
    ret = []
    for i in range(len(typ.key_types)):
        arg_name = alc[i]
        key_type = typ.key_types[i]

        # Create `arg` node
        if include_type:
            arg_node = vy_ast.arg(
                node_id=context.reserve_id(),
                arg=arg_name,
                annotation=vy_ast.Name(node_id=context.reserve_id(), id=str(key_type)),
            )
        else:
            arg_node = generate_name_node(context.reserve_id(), arg_name)

        arg_node._metadata["type"] = key_type
        ret.append(arg_node)
    return ret


def get_mapping_var_name(node: vy_ast.Subscript) -> str:
    """
    Helper function to get the contract variable name for a mapping.
    """
    if isinstance(node.value, vy_ast.Attribute):
        return node.value.attr
    elif isinstance(node.value, vy_ast.Subscript):
        return get_mapping_var_name(node.value)
    raise
