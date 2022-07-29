from vyro.exceptions import UnsupportedNode
from vyro.transpiler.visitor import BaseVisitor


class UnsupportedVisitor(BaseVisitor):
    def visit_ImportFrom(self, node, ast, context):
        raise UnsupportedNode(f"{type(node)} is not supported yet.", node)
