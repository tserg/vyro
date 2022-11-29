import copy
from typing import List

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

    def _write_memory_array_to_storage(
        self,
        storage_var_name: str,
        context: ASTContext,
        stmt_node: vy_ast.VyperNode,
        scope_node: vy_ast.VyperNode,
        scope_node_body: List[vy_ast.VyperNode],
        value_node: vy_ast.VyperNode,
        vy_typ: ArrayDefinition,
        idx_list: List[int],
    ):
        """
        Helper function to append statements to write a declared memory array to storage
        to the body of the given scope node.

        This function recursively visits a List node in a depth-first manner, since
        the AST tree for a nested array is declared in the reverse manner.
        """
        if isinstance(value_node, vy_ast.List):
            # Visit nested list first
            for idx, element in enumerate(value_node.elements):
                new_idx_list = copy.deepcopy(idx_list)
                new_idx_list.append(idx)
                self._write_memory_array_to_storage(
                    storage_var_name,
                    context,
                    stmt_node,
                    scope_node,
                    scope_node_body,
                    element,
                    vy_typ,
                    new_idx_list,
                )

        else:
            # Index are reversed: a[i][j] is arranged as j as outer and i as nested subscript
            # We loop through the list construct the nodes from most nested to top level
            nested_value_node = None
            while len(idx_list) > 0:

                next_idx = idx_list.pop(0)

                # Create the index node and assign the value
                value_node_dup = type(value_node).from_node(value_node, value=value_node.value)
                value_node_dup.node_id = context.reserve_id()

                if nested_value_node is None:
                    # Create final subscript
                    self_address_node = create_name_node(context, name="self")
                    self_address_node._metadata["type"] = AddressDefinition()

                    var_decl_ref_node = vy_ast.Attribute(
                        node_id=context.reserve_id(),
                        attr=storage_var_name,
                        value=self_address_node,
                        ast_type="Attribute",
                    )
                    var_decl_ref_node._metadata["type"] = vy_typ
                    set_parent(self_address_node, var_decl_ref_node)

                    nested_value_node = var_decl_ref_node

                idx_node = vy_ast.Int(
                    node_id=context.reserve_id(),
                    value=next_idx,
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
                    value=nested_value_node,
                    ast_type="Subscript",
                )
                set_parent(index_node, subscript_node)
                set_parent(nested_value_node, subscript_node)

                # Update nested value node to the latest created Subscript node
                nested_value_node = subscript_node

                if len(idx_list) == 0:
                    # Add statement to AST when index list is exhausted
                    vy_storage_write_node = create_assign_node(
                        context,
                        targets=[subscript_node],
                        value=value_node_dup,
                    )
                    vy_storage_write_node.target._metadata["type"] = vy_typ
                    insert_statement_after(
                        vy_storage_write_node, stmt_node, scope_node, scope_node_body
                    )
                    break

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
        stmt_node = get_stmt_node(node)
        scope_node, scope_node_body = get_scope(node)
        self._write_memory_array_to_storage(
            var_decl_name, context, stmt_node, scope_node, scope_node_body, node.value, vy_typ, []
        )

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
