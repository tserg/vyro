from vyper import ast as vy_ast

from vyro.exceptions import UnsupportedNode, UnsupportedType
from vyro.transpiler.context import ASTContext
from vyro.transpiler.visitor import BaseVisitor


class UnsupportedVisitor(BaseVisitor):
    def _visit_unsupported_node(self, node: vy_ast.VyperNode):
        raise UnsupportedNode(f"{type(node)} is not supported.", node)

    def visit_For(self, node: vy_ast.For, ast: vy_ast.Module, context: ASTContext):
        self._visit_unsupported_node(node)

    def visit_StructDef(self, node: vy_ast.StructDef, ast: vy_ast.Module, context: ASTContext):
        raise UnsupportedType("Structs are not supported.", node)
