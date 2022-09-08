from vyper import ast as vy_ast
from vyper.semantics.types.bases import DataLocation
from vyper.semantics.types.utils import get_type_from_annotation

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import get_cairo_type
from vyro.transpiler.visitor import BaseVisitor


class ArgsConverterVisitor(BaseVisitor):
    """
    Retrieve the type for a `vy_ast.arg` node and set it to its Cairo type
    """

    def visit_arg(self, node: vy_ast.arg, ast: vy_ast.Module, context: ASTContext):
        if node._metadata.get("type") is not None:
            return

        vyper_typ = get_type_from_annotation(node.annotation, DataLocation.UNSET)
        cairo_typ = get_cairo_type(vyper_typ)

        if isinstance(cairo_typ, CairoUint256Definition):
            add_builtin_to_module(ast, "Uint256")

        node._metadata["type"] = cairo_typ
