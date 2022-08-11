from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.visitor import BaseVisitor
from vyro.transpiler.utils import convert_node_type_definition
from vyro.exceptions import FeltOverflowException


class ConstantHandlerVisitor(BaseVisitor):
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
