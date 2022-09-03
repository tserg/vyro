from vyro.exceptions import UnsupportedNode, UnsupportedType
from vyro.transpiler.visitor import BaseVisitor


class UnsupportedVisitor(BaseVisitor):
    def _visit_unsupported_node(self, node):
        raise UnsupportedNode(f"{type(node)} is not supported.", node)

    def visit_EnumDef(self, node, ast, context):
        self._visit_unsupported_node(node)

    def visit_For(self, node, ast, context):
        self._visit_unsupported_node(node)

    def visit_StructDef(self, node, ast, context):
        raise UnsupportedType("Structs are not supported.", node)
