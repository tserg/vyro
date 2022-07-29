from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.visitor import BaseVisitor


class CairoImporterVisitor(BaseVisitor):
    def visit_Module(self, node, ast, context):
        # Add import for hash builtin
        add_builtin_to_module(ast, "HashBuiltin")

        for i in node.body:
            self.visit(i, ast, context)

    def visit_AnnAssign(self, node, ast, context):
        type_ = node._metadata.get("type")
        if isinstance(type_, CairoUint256Definition):
            add_builtin_to_module(ast, "Uint256")

    def visit_VariableDecl(self, node, ast, context):
        type_ = node._metadata.get("type")
        if isinstance(type_, CairoUint256Definition):
            add_builtin_to_module(ast, "Uint256")
