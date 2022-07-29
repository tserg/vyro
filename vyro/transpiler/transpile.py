from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.passes import (
    InitialisationVisitor,
    StorageVarVisitor,
    TestVisitor,
    UnsupportedVisitor,
)

PASSES = {
    "U": TestVisitor,
    "I": InitialisationVisitor,
    "Fc": UnsupportedVisitor,
    "Sv": StorageVarVisitor,
}


def transpile(ast: vy_ast.Module):
    ctx = ASTContext.get_context(ast)
    for k, v in PASSES.items():
        visitor = v()
        visitor.visit(ast, ast, ctx)
