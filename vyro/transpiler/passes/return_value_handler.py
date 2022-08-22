from vyper import ast as vy_ast

from vyro.transpiler.utils import generate_name_node, get_cairo_type, insert_statement_before
from vyro.transpiler.visitor import BaseVisitor


class ReturnValueHandler(BaseVisitor):
    """
    Replaces the return value with a local variable if it is an expression.
    """

    def visit_FunctionDef(self, node, ast, context):
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

        return_node = return_nodes.pop()
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
            assign_return_value._children.add(temp_name_node)
            assign_return_value._children.add(return_value_node)

            # Add new `Assign` node to function body
            insert_statement_before(assign_return_value, return_node, node)
            node._children.add(assign_return_value)

            # Assign temporary variable as the return value
            return_name_node = vy_ast.Name(
                node_id=context.reserve_id(), id=temp_name_node.id, ast_type="Name"
            )
            return_name_node._metadata["type"] = return_cairo_typ
            return_node.value = return_name_node
            return_node._children.add(return_name_node)
