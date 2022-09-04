from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.visitor import BaseVisitor


class CairoImporterVisitor(BaseVisitor):
    def visit(self, node, ast, context):
        type_ = node._metadata.get("type")
        if isinstance(type_, CairoUint256Definition):
            add_builtin_to_module(ast, "Uint256")

        super().visit(node, ast, context)

    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):
        fn_typ = node._metadata.get("type")

        return_typ = fn_typ.return_type
        if isinstance(return_typ, CairoUint256Definition):
            add_builtin_to_module(ast, "Uint256")

        super().visit_FunctionDef(node, ast, context)

    def visit_Module(self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext):
        # Add import for hash builtin
        add_builtin_to_module(ast, "HashBuiltin")

        for i in node.body:
            self.visit(i, ast, context)
