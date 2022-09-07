from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.passes.builtin_constants.block_constant_handler import (
    BlockConstantHandlerVisitor,
)
from vyro.transpiler.passes.builtin_constants.msg_sender_converter import MsgSenderConverterVisitor
from vyro.transpiler.visitor import BaseVisitor

PASSES = [MsgSenderConverterVisitor(), BlockConstantHandlerVisitor()]


class BuiltinConstantHandlerVisitor(BaseVisitor):
    def visit_Module(self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext):
        for v in PASSES:
            v.visit(node, ast, context)
