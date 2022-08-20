from vyper import ast as vy_ast
from vyper.semantics.types.bases import DataLocation
from vyper.semantics.types.utils import get_type_from_annotation

from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import get_cairo_type
from vyro.transpiler.visitor import BaseVisitor


class EventHandlerVisitor(BaseVisitor):
    def visit_EventDef(
        self, node: vy_ast.EventDef, ast: vy_ast.Module, context: ASTContext
    ):
        for i in node.body:
            vyper_typ = get_type_from_annotation(i.annotation, DataLocation.UNSET)
            cairo_typ = get_cairo_type(vyper_typ)
            i._metadata["type"] = cairo_typ
