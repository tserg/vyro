from typing import Dict, Set

from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.visitor import BaseVisitor


class InitialisationVisitor(BaseVisitor):
    def visit_Module(
        self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext
    ):
        # Initialise import directives
        node._metadata["import_directives"]: Dict[str, Set[str]] = {}

        for i in node.body:
            self.visit(i, ast, context)
