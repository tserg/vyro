from vyper import ast as vy_ast
from vyper.semantics.types.user.enum import EnumDefinition

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    add_implicit_to_function,
    generate_name_node,
    get_scope,
    get_stmt_node,
    insert_statement_before,
    set_parent,
    wrap_operation_in_call,
)
from vyro.transpiler.visitor import BaseVisitor


class EnumConverterVisitor(BaseVisitor):
    def visit_Compare(self, node: vy_ast.EnumDef, ast: vy_ast.Module, context: ASTContext):
        op = node.op
        if not isinstance(op, (vy_ast.In, vy_ast.NotIn)):
            return

        left_typ = node.left._metadata["type"]
        if isinstance(left_typ, EnumDefinition):
            members_len = len(left_typ.members)
            if members_len <= 251:
                bitwise_and_op = "bitwise_and"
                is_zero_op = "vyro_is_zero"
            else:
                bitwise_and_op = "uint256_and"
                is_zero_op = "vyro_uint256_is_zero"

            add_builtin_to_module(ast, bitwise_and_op)
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, is_zero_op)

            out_cairo_typ = FeltDefinition()

            # perform bitwise and
            bitwise_and_name_node = generate_name_node(context.reserve_id())
            bitwise_and_name_node._metadata["type"] = out_cairo_typ

            wrapped_bitwise_and_call = wrap_operation_in_call(
                ast,
                context,
                bitwise_and_op,
                args=[node.left, node.right],
            )
            wrapped_bitwise_and_call._metadata["type"] = out_cairo_typ
            node._children.remove(node.left)
            node._children.remove(node.right)
            set_parent(node.left, wrapped_bitwise_and_call)
            set_parent(node.right, wrapped_bitwise_and_call)

            bitwise_assign = vy_ast.Assign(
                node_id=context.reserve_id(),
                targets=[bitwise_and_name_node],
                value=wrapped_bitwise_and_call,
                ast_type="Assign",
            )
            bitwise_assign._metadata["type"] = out_cairo_typ
            set_parent(bitwise_and_name_node, bitwise_assign)
            set_parent(wrapped_bitwise_and_call, bitwise_assign)

            stmt_node = get_stmt_node(node)
            scope_node, scope_node_body = get_scope(node)
            insert_statement_before(bitwise_assign, stmt_node, scope_node, scope_node_body)

            # perform is zero
            bitwise_and_name_node_dup = generate_name_node(
                context.reserve_id(), name=bitwise_and_name_node.id
            )

            is_zero_name_node = generate_name_node(context.reserve_id())
            is_zero_name_node._metadata["type"] = out_cairo_typ

            wrapped_is_zero_call = wrap_operation_in_call(
                ast,
                context,
                is_zero_op,
                args=[bitwise_and_name_node_dup],
            )
            set_parent(bitwise_and_name_node_dup, wrapped_is_zero_call)
            wrapped_is_zero_call._metadata["type"] = out_cairo_typ

            is_zero_assign = vy_ast.Assign(
                node_id=context.reserve_id(),
                targets=[is_zero_name_node],
                value=wrapped_is_zero_call,
                ast_type="Assign",
            )
            is_zero_assign._metadata["type"] = out_cairo_typ
            set_parent(is_zero_name_node, is_zero_assign)
            set_parent(wrapped_is_zero_call, is_zero_assign)

            insert_statement_before(is_zero_assign, stmt_node, scope_node, scope_node_body)

            # perform additional is zero check for `In`
            if isinstance(op, vy_ast.In):
                is_zero_name_node_dup = generate_name_node(
                    context.reserve_id(), name=is_zero_name_node.id
                )

                is_zero_name_node = generate_name_node(context.reserve_id())
                is_zero_name_node._metadata["type"] = out_cairo_typ

                wrapped_is_zero_call = wrap_operation_in_call(
                    ast,
                    context,
                    is_zero_op,
                    args=[is_zero_name_node_dup],
                )
                set_parent(is_zero_name_node_dup, wrapped_is_zero_call)
                wrapped_is_zero_call._metadata["type"] = out_cairo_typ

                is_zero_assign = vy_ast.Assign(
                    node_id=context.reserve_id(),
                    targets=[is_zero_name_node],
                    value=wrapped_is_zero_call,
                    ast_type="Assign",
                )
                is_zero_assign._metadata["type"] = out_cairo_typ
                set_parent(is_zero_name_node, is_zero_assign)
                set_parent(wrapped_is_zero_call, is_zero_assign)

                insert_statement_before(is_zero_assign, stmt_node, scope_node, scope_node_body)

            replacement_name_node = generate_name_node(
                context.reserve_id(), name=is_zero_name_node.id
            )
            replacement_name_node._metadata["type"] = out_cairo_typ

            ast.replace_in_tree(node, replacement_name_node)

    def visit_EnumDef(self, node: vy_ast.EnumDef, ast: vy_ast.Module, context: ASTContext):
        enum_name = node.name
        members_len = len(node.body)
        cairo_typ = FeltDefinition() if members_len <= 251 else CairoUint256Definition()

        count = 0
        for member in node.body:
            member_name = member.value.id
            int_value = 2**count
            count += 1

            # Replace enum with integer values
            member_references = ast.get_descendants(
                vy_ast.Attribute, {"attr": member_name, "value.id": enum_name}
            )

            for r in member_references:
                replacement_int = vy_ast.Int(
                    node_id=context.reserve_id(),
                    value=int_value,
                )
                replacement_int._metadata["type"] = cairo_typ
                ast.replace_in_tree(r, replacement_int)

            type_references = ast.get_descendants(vy_ast.arg, {"annotation.id": enum_name})
            for t in type_references:
                t.annotation.id = "Uint256"
                t._metadata["type"] = cairo_typ

    def visit_Module(self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext):
        # visit `Compare` nodes first to convert membership comparisons to bitwise ops
        # before the Vyper enum type definition is changed to the Cairo equivalent
        compares = node.get_descendants(vy_ast.Compare)

        for c in compares:
            self.visit(c, ast, context)

        super().visit_Module(node, ast, context)