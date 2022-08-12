from vyper import ast as vy_ast

from vyro.exceptions import FeltOverflowException
from vyro.transpiler.utils import convert_node_type_definition, replace_in_tree
from vyro.transpiler.visitor import BaseVisitor
from vyro.utils.utils import CAIRO_PRIME


class ConstantHandlerVisitor(BaseVisitor):
    def _assert_valid_felt(self, node, int_value):
        if int_value > CAIRO_PRIME:
            raise FeltOverflowException(
                f"Value of constant ({node.value}) exceeds maximum felt value ({CAIRO_PRIME})",
                node,
            )

    def visit_Module(self, node, ast, context):
        # Visit contract variable declarations only
        contract_vars = [i for i in node.body if isinstance(i, vy_ast.VariableDecl)]
        for c in contract_vars:
            self.visit(c, ast, context)

    def visit_VariableDecl(self, node, ast, context):
        # Early termination if not a constant
        if not node.is_constant:
            return

        convert_node_type_definition(node)
        self.visit(node.value, ast, context)

    def visit_Hex(self, node, ast, context):
        # Get integer value
        hex_value = node.value
        int_value = int(hex_value, 16)

        # Replace with integer node
        replacement_int = vy_ast.Int.from_node(node, value=int_value)

        self._assert_valid_felt(node, int_value)

        replace_in_tree(ast, node, replacement_int)

        # Search for folded nodes
        for n in ast.get_descendants(vy_ast.Hex, {"value": hex_value}, reverse=True):
            new_replacement_int = vy_ast.Int.from_node(n, value=int_value)
            replace_in_tree(ast, n, new_replacement_int)

    def visit_Int(self, node, ast, context):
        int_value = node.value
        self._assert_valid_felt(node, int_value)

        # Get type from parent `VariableDecl`
        # parent = node.get_ancestor(vy_ast.VariableDecl)
        # typ = parent._metadata.get("type")
        # cairo_typ = get_cairo_type(typ)

        # Propagate type for folded nodes for `uint256_handler` pass
        # for n in ast.get_descendants(vy_ast.Int, {"value": int_value}, reverse=True):
        #    n._metadata["type"] = cairo_typ
