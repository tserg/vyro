from typing import Dict, Set

from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.visitor import BaseVisitor
from vyro.transpiler.utils import initialise_function_implicits


class InitialisationVisitor(BaseVisitor):
    def visit_FunctionDef(
        self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext
    ):
        # Initialise implicits
        initialise_function_implicits(node)

    def visit_Module(
        self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext
    ):
        # Initialise import directives
        node._metadata["import_directives"]: Dict[str, Set[str]] = {}

        for i in node.body:
            self.visit(i, ast, context)
