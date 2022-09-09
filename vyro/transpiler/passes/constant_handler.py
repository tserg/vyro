from vyper import ast as vy_ast
from vyper.utils import bytes_to_int, hex_to_int

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.exceptions import FeltOverflowException
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import convert_node_type_definition, generate_name_node
from vyro.transpiler.visitor import BaseVisitor
from vyro.utils.utils import CAIRO_PRIME

STR_LIMIT = 31


class ConstantHandlerVisitor(BaseVisitor):
    def _assert_valid_felt(self, node: vy_ast.Constant, int_value: int):
        if int_value > CAIRO_PRIME:
            raise FeltOverflowException(
                f"Value of constant ({node.value}) exceeds maximum felt value ({CAIRO_PRIME})", node
            )

    def visit_Bytes(self, node: vy_ast.Bytes, ast: vy_ast.Module, context: ASTContext):
        # Get integer value
        byte_value = node.value
        int_value = bytes_to_int(byte_value)

        self._assert_valid_felt(node, int_value)

        # Search for folded nodes
        for n in ast.get_descendants(vy_ast.Bytes, {"value": byte_value}, reverse=True):
            replacement_int = vy_ast.Int.from_node(n, value=int_value)
            ast.replace_in_tree(n, replacement_int)

    def visit_Hex(self, node: vy_ast.Hex, ast: vy_ast.Module, context: ASTContext):
        # Get integer value
        hex_value = node.value
        int_value = hex_to_int(hex_value)

        self._assert_valid_felt(node, int_value)

        # Search for folded nodes
        for n in ast.get_descendants(vy_ast.Hex, {"value": hex_value}, reverse=True):
            # Replace with integer node
            replacement_int = vy_ast.Int.from_node(node, value=int_value)
            ast.replace_in_tree(n, replacement_int)

    def visit_Int(self, node: vy_ast.Int, ast: vy_ast.Module, context: ASTContext):
        int_value = node.value
        self._assert_valid_felt(node, int_value)

    def visit_Log(self, node: vy_ast.Log, ast: vy_ast.Module, context: ASTContext):
        self.visit(node.value, ast, context)

    def visit_Module(self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext):
        # Visit contract variable declarations and functions only
        contract_vars = [
            i for i in node.body if isinstance(i, (vy_ast.FunctionDef, vy_ast.VariableDecl))
        ]
        for c in contract_vars:
            self.visit(c, ast, context)

    def visit_NameConstant(
        self, node: vy_ast.NameConstant, ast: vy_ast.Module, context: ASTContext
    ):
        bool_value = node.value

        # Convert boolean value to string
        bool_str = str(bool_value).upper()

        # Add builtin
        add_builtin_to_module(ast, bool_str)

        # Search for folded nodes
        for n in ast.get_descendants(vy_ast.NameConstant, {"value": bool_value}, reverse=True):
            replacement_node = generate_name_node(context, name=bool_str)
            ast.replace_in_tree(n, replacement_node)

    def visit_Str(self, node: vy_ast.Str, ast: vy_ast.Module, context: ASTContext):
        str_value = node.value
        if len(str_value) > STR_LIMIT:
            raise FeltOverflowException(
                f"Strings cannot exceed {STR_LIMIT} characters in length", node
            )

    def visit_VariableDecl(
        self, node: vy_ast.VariableDecl, ast: vy_ast.Module, context: ASTContext
    ):
        # Early termination if not a constant
        if node.is_constant is False:
            return

        convert_node_type_definition(node)

        super().visit_VariableDecl(node, ast, context)
