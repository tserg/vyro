from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    generate_name_node,
    get_cairo_type,
    get_scope,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class ReturnValueHandler(BaseVisitor):
    """
    Replaces the return value with a local variable if it is an expression.
    """

    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):
        fn_typ = node._metadata["type"]

        return_type = fn_typ.return_type
        if return_type is None:
            return

        # Convert return type to Cairo type
        return_cairo_typ = get_cairo_type(return_type)
        fn_typ.return_type = return_cairo_typ

        # Check for `Return` node in body
        return_nodes = node.get_descendants(vy_ast.Return)
        if len(return_nodes) == 0:
            return

        for return_node in return_nodes:
            if not isinstance(return_node.value, vy_ast.Name):
                # Store return value node
                return_value_node = return_node.value

                # Remove return value node from `Return` node`
                return_node._children.remove(return_value_node)

                # Assign return value to a temporary variable
                temp_name_node = generate_name_node(context.reserve_id())
                temp_name_node._metadata["type"] = return_cairo_typ

                assign_return_value = vy_ast.Assign(
                    node_id=context.reserve_id(),
                    targets=[temp_name_node],
                    value=return_value_node,
                    ast_type="Assign",
                )

                assign_return_value._metadata["type"] = return_cairo_typ
                set_parent(temp_name_node, assign_return_value)
                set_parent(return_value_node, assign_return_value)

                # Add new `Assign` node to function body
                scope_node, scope_node_body = get_scope(return_node)
                insert_statement_before(
                    assign_return_value, return_node, scope_node, scope_node_body
                )
                set_parent(assign_return_value, node)

                # Assign temporary variable as the return value
                return_name_node = vy_ast.Name(
                    node_id=context.reserve_id(), id=temp_name_node.id, ast_type="Name"
                )
                return_name_node._metadata["type"] = return_cairo_typ
                return_node.value = return_name_node
                set_parent(return_name_node, return_node)
