from vyper import ast as vy_ast
from vyper.builtin_functions.functions import get_builtin_functions

from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.exceptions import UnsupportedFeature
from vyro.transpiler.utils import get_cairo_type
from vyro.transpiler.visitor import BaseVisitor

VY_BUILTIN_FNS = get_builtin_functions()


class BuiltinFunctionHandlerVisitor(BaseVisitor):
    def _handle_empty(self, node, ast, context):
        # Get Vyper type
        vy_typ = node.args[0]._metadata["type"].typedef

        # Get Cairo type
        cairo_typ = get_cairo_type(vy_typ)

        # Create `Int` node
        replacement_node = vy_ast.Int(node_id=context.reserve_id(), value=0)

        if isinstance(cairo_typ, FeltDefinition):
            replacement_node._metadata["type"] = FeltDefinition()
        elif isinstance(cairo_typ, CairoUint256Definition):
            replacement_node._metadata["type"] = CairoUint256Definition()

        # Replace `Call` node
        ast.replace_in_tree(node, replacement_node)

    def visit_Call(self, node, ast, context):
        call_typ = node.func._metadata["type"]

        if not hasattr(call_typ, "_id"):
            return

        if call_typ._id in VY_BUILTIN_FNS:
            handle_fn = getattr(self, f"_handle_{call_typ._id}", None)
            if handle_fn is None:
                raise UnsupportedFeature(
                    f"{call_typ._id} builtin function is not supported", node
                )
            handle_fn(node, ast, context)
