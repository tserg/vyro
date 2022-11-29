from vyper import ast as vy_ast
from vyper.exceptions import UnknownType
from vyper.semantics.types.bases import DataLocation
from vyper.semantics.types.indexable.sequence import ArrayDefinition
from vyper.semantics.types.utils import get_type_from_annotation
from vyper.semantics.types.value.address import AddressDefinition

from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    convert_node_type_definition,
    create_assign_node,
    create_name_node,
    get_cairo_type,
    get_scope,
    get_stmt_node,
    insert_statement_after,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class StaticArrayConverterVisitor(BaseVisitor):
    """
    This pass converts static arrays into Cairo storage mappings.

    For example, reading `array[i][j]` is equivalent to `array_storage.read(i, j)`,
    and writing `array[i][j] = k` is equivalent to `array_storage.write(i, j, k)`.
    """

    def visit_AnnAssign(self, node: vy_ast.AnnAssign, ast: vy_ast.Module, context: ASTContext):
        """
        Convert memory static arrays to storage mappings.

        Example:

        Vyper:
            `a: uint8[3] = [2, 4, 6]`

        Cairo:
            `a.write(0, 2)`
            `a.write(1, 4)`
            `a.write(2, 6)`
        """
        try:
            vy_typ = get_type_from_annotation(node.annotation, DataLocation.UNSET)
        except UnknownType:
            # Skip structs because type cannot be derived without struct def being
            # properly initialised in namespace
            return

        if not isinstance(vy_typ, ArrayDefinition):
            return

        cairo_typ = get_cairo_type(vy_typ)

        # Create the storage mapping
        fn_name = node.get_ancestor(vy_ast.FunctionDef).name
        var_name = node.target.id
        var_decl_name = f"{fn_name}_{var_name}_MEM"

        var_decl_name_node = create_name_node(context, name=var_decl_name)
        var_decl_name_node._metadata["type"] = cairo_typ

        var_decl_node = vy_ast.VariableDecl(
            node_id=context.reserve_id(),
            target=var_decl_name_node,
            value=None,
            annotation=create_name_node(context, name=str(vy_typ)),
            ast_type="VariableDecl",
        )
        var_decl_node._metadata["type"] = cairo_typ

        set_parent(var_decl_name_node, var_decl_node)
        ast.add_to_body(var_decl_node)

        # Write the values to storage
        array_values = [n.value for n in node.value.elements]

        stmt_node = get_stmt_node(node)
        scope_node, scope_node_body = get_scope(node)

        for idx, v in enumerate(array_values):
            self_address_node = create_name_node(context, name="self")
            self_address_node._metadata["type"] = AddressDefinition()

            var_decl_ref_node = vy_ast.Attribute(
                node_id=context.reserve_id(),
                attr=var_decl_name,
                value=self_address_node,
                ast_type="Attribute",
            )
            var_decl_ref_node._metadata["type"] = vy_typ
            set_parent(self_address_node, var_decl_ref_node)

            idx_node = vy_ast.Int(
                node_id=context.reserve_id(),
                value=idx,
                ast_type="Int",
            )

            index_node = vy_ast.Index(
                node_id=context.reserve_id(),
                value=idx_node,
                ast_type="Index",
            )
            set_parent(idx_node, index_node)

            subscript_node = vy_ast.Subscript(
                node_id=context.reserve_id(),
                slice=index_node,
                value=var_decl_ref_node,
                ast_type="Subscript",
            )
            set_parent(index_node, subscript_node)
            set_parent(var_decl_ref_node, subscript_node)

            vy_storage_write_node = create_assign_node(
                context,
                targets=[subscript_node],
                value=vy_ast.Int(
                    node_id=context.reserve_id(),
                    value=v,
                    ast_type="Int",
                ),
            )

            vy_storage_write_node.target._metadata["type"] = vy_typ
            insert_statement_after(vy_storage_write_node, stmt_node, scope_node, scope_node_body)

        # Find references to the memory array and replace with storage mapping read
        array_references = scope_node.get_descendants(vy_ast.Subscript, {"value.id": var_name})
        for r in array_references:
            # Re-use existing index node with indexes
            index_node = r.slice
            r._children.remove(index_node)

            self_address_node = create_name_node(context, name="self")
            self_address_node._metadata["type"] = AddressDefinition()

            var_decl_ref_node = vy_ast.Attribute(
                node_id=context.reserve_id(),
                attr=var_decl_name,
                value=self_address_node,
                ast_type="Attribute",
            )

            var_decl_ref_node._metadata["type"] = vy_typ
            set_parent(self_address_node, var_decl_ref_node)

            subscript_node = vy_ast.Subscript(
                node_id=context.reserve_id(),
                slice=index_node,
                value=var_decl_ref_node,
                ast_type="Subscript",
            )
            set_parent(index_node, subscript_node)
            set_parent(var_decl_ref_node, subscript_node)

            ast.replace_in_tree(r, subscript_node)

        # Remove original AnnAssign node
        scope_node_body.remove(node)

    def visit_VariableDecl(
        self, node: vy_ast.VariableDecl, ast: vy_ast.Module, context: ASTContext
    ):
        vy_typ = node._metadata.get("type")
        if not isinstance(vy_typ, ArrayDefinition):
            return

        convert_node_type_definition(node)
