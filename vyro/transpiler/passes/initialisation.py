from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.visitor import BaseVisitor
from vyro.transpiler.utils import get_cairo_type, initialise_function_implicits


class InitialisationVisitor(BaseVisitor):
    def visit_AnnAssign(
        self, node: vy_ast.AnnAssign, ast: vy_ast.Module, context: ASTContext
    ):
        typ = node.target._metadata.get("type")
        cairo_typ = get_cairo_type(typ)
        node._metadata["type"] = cairo_typ

    def visit_AugAssign(
        self, node: vy_ast.AnnAssign, ast: vy_ast.Module, context: ASTContext
    ):
        typ = node.target._metadata.get("type")
        cairo_typ = get_cairo_type(typ)
        node._metadata["type"] = cairo_typ

    def visit_FunctionDef(
        self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext
    ):
        # Initialise implicits
        initialise_function_implicits(node)

        for i in node.body:
            self.visit(i, ast, context)

    def visit_Module(
        self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext
    ):
        # Initialise import directives
        node._metadata["import_directives"] = {}

        for i in node.body:
            self.visit(i, ast, context)
