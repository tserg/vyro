import json

from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.passes import (
    AssertHandlerVisitor,
    BuiltinConstantHandlerVisitor,
    BuiltinFunctionHandlerVisitor,
    CairoImporterVisitor,
    ConstantHandlerVisitor,
    ConstructorHandler,
    EventHandlerVisitor,
    IfHandlerVisitor,
    InitialisationVisitor,
    InternalFunctionsHandler,
    MsgSenderConverterVisitor,
    OpsConverterVisitor,
    ReturnValueHandler,
    StorageVarVisitor,
    Uint256HandlerVisitor,
    UnsupportedVisitor,
)

PASSES = {
    "Fc": UnsupportedVisitor,
    "I": InitialisationVisitor,
    "IfH": IfHandlerVisitor,
    "Ms": MsgSenderConverterVisitor,
    "BC": BuiltinConstantHandlerVisitor,
    "Bf": BuiltinFunctionHandlerVisitor,
    "Ch": ConstructorHandler,
    "Ev": EventHandlerVisitor,
    "Ah": AssertHandlerVisitor,
    "If": InternalFunctionsHandler,
    "Rv": ReturnValueHandler,
    "Sv": StorageVarVisitor,
    "Oc": OpsConverterVisitor,
    "Co": ConstantHandlerVisitor,
    "Ui": Uint256HandlerVisitor,
    "CI": CairoImporterVisitor,
}


def transpile(ast: vy_ast.Module, print_tree: bool = False):
    ctx = ASTContext.get_context(ast)
    for k, v in PASSES.items():
        visitor = v()
        visitor.visit(ast, ast, ctx)

        if print_tree is True:
            ast_dict = ast.to_dict()
            print(f"\n\n=============== Transpiled AST - {v} ===============\n\n")
            print(json.dumps(ast_dict, sort_keys=True, indent=4))
