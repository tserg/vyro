from vyro.exceptions import UnsupportedFeature
from vyro.transpiler.visitor import BaseVisitor


class UnsupportedVisitor(BaseVisitor):
    def visit_VariableDecl(self, node, ast, context):
        if node.is_immutable:
            raise UnsupportedFeature("Immutables are not supported in Cairo", node)
