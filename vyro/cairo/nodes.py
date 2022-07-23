from vyper import ast as vy_ast
from vyper.ast.nodes import FunctionDef, VyperNode


class CairoStorageWrite(vy_ast.Assign):
    """Wrapper class for Cairo write to storage"""


class CairoStorageRead(vy_ast.Assign):
    """Wrapper class for Cairo read from storage"""
