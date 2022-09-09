from vyper import ast as vy_ast
from vyper.semantics.types.user.enum import EnumDefinition

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    add_implicit_to_function,
    create_assign_node,
    create_call_node,
    create_name_node,
    get_cairo_type,
    get_scope,
    get_stmt_node,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class EnumConverterVisitor(BaseVisitor):
    """
    This pass converts enums into integers, and transforms membership comparisons
    of enums into bitwise operations.

    Enums with 251 or less members are converted to felts. Otherwise, they are
    converted to Uint256.
    """

    def visit(self, node: vy_ast.VyperNode, ast: vy_ast.Module, context: ASTContext):
        vyper_typ = node._metadata.get("type")
        if isinstance(vyper_typ, EnumDefinition):
            cairo_typ = get_cairo_type(vyper_typ)
            node._metadata["type"] = cairo_typ

        super().visit(node, ast, context)

    def visit_Compare(self, node: vy_ast.EnumDef, ast: vy_ast.Module, context: ASTContext):
        op = node.op
        if not isinstance(op, (vy_ast.In, vy_ast.NotIn)):
            return

        left_typ = node.left._metadata.get("type")
        if not isinstance(left_typ, EnumDefinition):
            return

        out_cairo_typ = get_cairo_type(left_typ)
        if isinstance(out_cairo_typ, FeltDefinition):
            bitwise_and_op = "bitwise_and"
            is_zero_op = "vyro_is_zero"
        elif isinstance(out_cairo_typ, CairoUint256Definition):
            bitwise_and_op = "uint256_and"
            is_zero_op = "vyro_uint256_is_zero"

        add_builtin_to_module(ast, bitwise_and_op)
        add_implicit_to_function(node, "bitwise_ptr")
        add_builtin_to_module(ast, is_zero_op)

        # perform bitwise and
        bitwise_and_name_node = create_name_node(context)
        bitwise_and_name_node._metadata["type"] = out_cairo_typ

        wrapped_bitwise_and_call = create_call_node(
            context, bitwise_and_op, args=[node.left, node.right]
        )
        wrapped_bitwise_and_call._metadata["type"] = out_cairo_typ
        node._children.remove(node.left)
        node._children.remove(node.right)
        set_parent(node.left, wrapped_bitwise_and_call)
        set_parent(node.right, wrapped_bitwise_and_call)

        bitwise_assign = create_assign_node(
            context,
            [bitwise_and_name_node],
            wrapped_bitwise_and_call,
        )
        bitwise_assign._metadata["type"] = out_cairo_typ

        stmt_node = get_stmt_node(node)
        scope_node, scope_node_body = get_scope(node)
        insert_statement_before(bitwise_assign, stmt_node, scope_node, scope_node_body)

        # perform is zero
        bitwise_and_name_node_dup = create_name_node(context, name=bitwise_and_name_node.id)

        is_zero_name_node = create_name_node(context)
        is_zero_name_node._metadata["type"] = FeltDefinition()

        wrapped_is_zero_call = create_call_node(
            context, is_zero_op, args=[bitwise_and_name_node_dup]
        )
        set_parent(bitwise_and_name_node_dup, wrapped_is_zero_call)
        wrapped_is_zero_call._metadata["type"] = FeltDefinition()

        is_zero_assign = create_assign_node(
            context,
            [is_zero_name_node],
            wrapped_is_zero_call,
        )
        is_zero_assign._metadata["type"] = FeltDefinition()

        insert_statement_before(is_zero_assign, stmt_node, scope_node, scope_node_body)

        # perform additional is zero check for `In`
        if isinstance(op, vy_ast.In):
            is_zero_name_node_dup = create_name_node(context, name=is_zero_name_node.id)

            is_zero_name_node = create_name_node(context)
            is_zero_name_node._metadata["type"] = FeltDefinition()

            wrapped_is_zero_call = create_call_node(
                context, "vyro_is_zero", args=[is_zero_name_node_dup]
            )
            add_builtin_to_module(ast, "vyro_is_zero")
            set_parent(is_zero_name_node_dup, wrapped_is_zero_call)
            wrapped_is_zero_call._metadata["type"] = FeltDefinition()

            is_zero_assign = create_assign_node(
                context,
                [is_zero_name_node],
                wrapped_is_zero_call,
            )
            is_zero_assign._metadata["type"] = FeltDefinition()

            insert_statement_before(is_zero_assign, stmt_node, scope_node, scope_node_body)

        replacement_name_node = create_name_node(context, name=is_zero_name_node.id)
        replacement_name_node._metadata["type"] = FeltDefinition()

        ast.replace_in_tree(node, replacement_name_node)

    def visit_EnumDef(self, node: vy_ast.EnumDef, ast: vy_ast.Module, context: ASTContext):
        enum_name = node.name
        members_len = len(node.body)
        cairo_typ = FeltDefinition() if members_len <= 251 else CairoUint256Definition()

        is_uint256 = False if members_len <= 251 else True

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
                if not is_uint256:
                    replacement_int = vy_ast.Int(node_id=context.reserve_id(), value=int_value)
                    replacement_int._metadata["type"] = cairo_typ
                else:
                    lo = int_value & ((1 << 128) - 1)
                    hi = int_value >> 128

                    # Cast literals as Uint256
                    keywords = [
                        vy_ast.keyword(
                            node_id=context.reserve_id(),
                            arg="low",
                            value=vy_ast.Int(
                                node_id=context.reserve_id(), value=lo, ast_type="Int"
                            ),
                            ast_type="keyword",
                        ),
                        vy_ast.keyword(
                            node_id=context.reserve_id(),
                            arg="high",
                            value=vy_ast.Int(
                                node_id=context.reserve_id(), value=hi, ast_type="Int"
                            ),
                            ast_typ="keyword",
                        ),
                    ]
                    replacement_int = create_call_node(context, "Uint256", keywords=keywords)
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
