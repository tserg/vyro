from vyper import ast as vy_ast

from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.visitor import BaseVisitor
from vyro.transpiler.utils import convert_node_type_definition
from vyro.exceptions import FeltOverflowException


class ConstantHandlerVisitor(BaseVisitor):
    def visit_Module(self, node, ast, context):
        # Visit contract variable declarations only
        contract_vars = [i for i in node.body if isinstance(i, vy_ast.VariableDecl)]
        for c in contract_vars:
            self.visit(c, ast, context)

    def visit_VariableDecl(self, node, ast, context):
        # Early termination if not a constant
        if not node.is_constant:
            return

        cairo_typ = convert_node_type_definition(node)
        if isinstance(cairo_typ, CairoUint256Definition):
            raise FeltOverflowException(
                "Constants of Uint256 type cannot be represented as a felt constant",
                node,
            )

        self.visit(node.value, ast, context)

    def visit_Hex(self, node, ast, context):
        # Get integer value
        hex_value = node.value
        int_value = int(hex_value, 16)

        # Replace with integer node
        replacement_int = vy_ast.Int.from_node(
            node,
            value=int_value,
        )

        ast.replace_in_tree(node, replacement_int)

        # Search for folded nodes
        for n in ast.get_descendants(vy_ast.Hex, {"value": hex_value}, reverse=True):
            new_replacement_int = vy_ast.Int.from_node(
                n,
                value=int_value,
            )
            ast.replace_in_tree(n, new_replacement_int)
