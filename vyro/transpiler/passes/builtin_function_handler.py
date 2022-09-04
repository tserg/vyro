import copy

from vyper import ast as vy_ast
from vyper.builtin_functions.functions import get_builtin_functions
from vyper.semantics.types.abstract import IntegerAbstractType, SignedIntegerAbstractType
from vyper.utils import int_bounds

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.exceptions import UnsupportedFeature
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    generate_name_node,
    get_cairo_type,
    get_scope,
    get_stmt_node,
    insert_statement_after,
    insert_statement_before,
    set_parent,
    wrap_operation_in_call,
)
from vyro.transpiler.visitor import BaseVisitor

VY_BUILTIN_FNS = get_builtin_functions()


class BuiltinFunctionHandlerVisitor(BaseVisitor):
    def _handle_convert(self, node, ast, context):
        in_vy_typ = node.args[0]._metadata.get("type")
        # Cast to Uint256 if out type is `uint256`
        out_vy_typ = node.args[1]._metadata["type"].typedef
        out_cairo_typ = get_cairo_type(out_vy_typ)

        if isinstance(in_vy_typ, IntegerAbstractType) and isinstance(
            out_vy_typ, IntegerAbstractType
        ):
            if isinstance(out_cairo_typ, CairoUint256Definition):
                # Wrap source value in a `felt_to_uint256` call
                wrapped_call_node = wrap_operation_in_call(
                    ast, context, "felt_to_uint256", args=[node.args[0]]
                )

                # Temporarily assign to a `Name` node
                temp_name_node = generate_name_node(context.reserve_id())
                temp_name_node._metadata["type"] = out_cairo_typ

                temp_assign_node = vy_ast.Assign(
                    node_id=context.reserve_id(), targets=[temp_name_node], value=wrapped_call_node
                )

                # Insert statement
                stmt_node = get_stmt_node(node)
                scope_node, scope_node_body = get_scope(node)
                insert_statement_before(temp_assign_node, stmt_node, scope_node, scope_node_body)

                # Add `felt_to_uint256` to imports
                add_builtin_to_module(ast, "felt_to_uint256")

                # Replace call node with temporary name node
                temp_name_node_dup = generate_name_node(
                    context.reserve_id(), name=temp_name_node.id
                )
                ast.replace_in_tree(node, temp_name_node_dup)

            else:
                # Unwrap `convert` call
                src = copy.deepcopy(node.args[0])
                ast.replace_in_tree(node, src)

                if in_vy_typ._bits > out_vy_typ._bits:
                    # Get bound values
                    lo, hi = int_bounds(out_vy_typ._is_signed, out_vy_typ._bits)

                    # Add clampers
                    hi_int = vy_ast.Int(node_id=context.reserve_id(), value=hi)
                    hi_clamper = wrap_operation_in_call(
                        ast, context, "assert_le", args=[src, hi_int]
                    )

                    lo_int = vy_ast.Int(node_id=context.reserve_id(), value=lo)
                    lo_clamper = wrap_operation_in_call(
                        ast, context, "assert_le", args=[lo_int, src]
                    )

                    # Add `assert_le` builtin
                    add_builtin_to_module(ast, "assert_le")

                    # Insert statements after
                    stmt_node = get_stmt_node(node)
                    scope_node, scope_node_body = get_scope(node)

                    if isinstance(stmt_node, vy_ast.Return):
                        insert_statement_before(lo_clamper, stmt_node, scope_node, scope_node_body)
                        insert_statement_before(hi_clamper, stmt_node, scope_node, scope_node_body)
                    else:
                        insert_statement_after(lo_clamper, stmt_node, scope_node, scope_node_body)
                        insert_statement_after(hi_clamper, stmt_node, scope_node, scope_node_body)
        else:
            raise UnsupportedFeature(
                f"Conversion of {in_vy_typ} to {out_vy_typ} is currently not supported", node
            )

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

    def _handle_max(self, node, ast, context):
        self._handle_minmax(node, ast, context, "max")

    def _handle_minmax(self, node, ast, context, fn_str):
        # Get Vyper type
        vy_typ = node._metadata["type"]

        # Get Cairo type
        cairo_typ = get_cairo_type(vy_typ)

        if isinstance(vy_typ, SignedIntegerAbstractType):
            raise UnsupportedFeature(f"`{fn_str}` is not supported for signed integers", node)

        if isinstance(cairo_typ, FeltDefinition):
            wrapped_op_str = f"vyro_{fn_str}"
        elif isinstance(cairo_typ, CairoUint256Definition):
            wrapped_op_str = f"{fn_str}256"

        add_builtin_to_module(ast, wrapped_op_str)

        wrapped_call_node = wrap_operation_in_call(ast, context, wrapped_op_str, args=node.args)
        wrapped_call_node._metadata["type"] = cairo_typ

        for a in node.args:
            set_parent(a, wrapped_call_node)

        ast.replace_in_tree(node, wrapped_call_node)

    def _handle_min(self, node, ast, context):
        self._handle_minmax(node, ast, context, "min")

    def visit_Call(self, node: vy_ast.Call, ast: vy_ast.Module, context: ASTContext):
        call_typ = node.func._metadata.get("type")

        if not hasattr(call_typ, "_id"):
            return

        if call_typ._id in VY_BUILTIN_FNS:
            handle_fn = getattr(self, f"_handle_{call_typ._id}", None)
            if handle_fn is None:
                raise UnsupportedFeature(f"{call_typ._id} builtin function is not supported", node)
            handle_fn(node, ast, context)
