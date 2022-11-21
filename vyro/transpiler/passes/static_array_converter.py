from vyper import ast as vy_ast
from vyper.semantics.types.indexable.sequence import ArrayDefinition

from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import convert_node_type_definition
from vyro.transpiler.visitor import BaseVisitor


class StaticArrayConverterVisitor(BaseVisitor):
    def visit_VariableDecl(self, node: vy_ast.VyperNode, ast: vy_ast.Module, context: ASTContext):
        vy_typ = node._metadata.get("type")
        if not isinstance(vy_typ, ArrayDefinition):
            return

        convert_node_type_definition(node)
