from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.exceptions import UnsupportedFeature
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    generate_name_node,
    get_cairo_type,
    get_scope,
    get_stmt_node,
    insert_statement_before,
    wrap_operation_in_call,
)
from vyro.transpiler.visitor import BaseVisitor


class BuiltinConstantHandlerVisitor(BaseVisitor):
    def visit_Attribute(self, node: vy_ast.Attribute, ast: vy_ast.Module, context: ASTContext):
        if not isinstance(node.value, vy_ast.Name):
            return

        if node.value.id != "block":
            return

        vy_typ = node._metadata["type"]
        cairo_typ = get_cairo_type(vy_typ)

        attr = node.attr
        val = node.value.id

        if val == "block":
            if attr == "timestamp":
                syscall_name = "get_block_timestamp"
                add_builtin_to_module(ast, "get_block_timestamp")
            elif attr == "number":
                syscall_name = "get_block_number"
                add_builtin_to_module(ast, "get_block_number")
            else:
                raise UnsupportedFeature(f"`block.{val}` is not supported.", node)

        # Insert syscall statement before current statement
        temp_name_node = generate_name_node(context.reserve_id())
        temp_name_node._metadata["type"] = FeltDefinition()

        syscall_node = wrap_operation_in_call(ast, context, syscall_name)
        assign_node = vy_ast.Assign(
            node_id=context.reserve_id(), targets=[temp_name_node], value=syscall_node
        )

        stmt_node = get_stmt_node(node)
        scope_node, scope_node_body = get_scope(stmt_node)

        insert_statement_before(assign_node, stmt_node, scope_node, scope_node_body)

        # Convert to Uint256
        if isinstance(cairo_typ, CairoUint256Definition):
            convert_name_node = generate_name_node(context.reserve_id())
            convert_name_node._metadata["type"] = cairo_typ

            convert_node = wrap_operation_in_call(
                ast, context, "felt_to_uint256", args=[temp_name_node]
            )
            add_builtin_to_module(ast, "felt_to_uint256")

            assign_node = vy_ast.Assign(
                node_id=context.reserve_id(), targets=[convert_name_node], value=convert_node
            )

            insert_statement_before(assign_node, stmt_node, scope_node, scope_node_body)
            temp_name_node = convert_name_node

        # Replace builtin constant with `Name` node
        temp_name_node_dup = generate_name_node(context.reserve_id(), name=temp_name_node.id)
        ast.replace_in_tree(node, temp_name_node_dup)
