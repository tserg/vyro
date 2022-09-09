from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.exceptions import UnsupportedOperation
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    add_implicit_to_function,
    convert_node_type_definition,
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

BINOP_TABLE = {
    # operation: [felt op, uint256 op]
    "modulus": ["vyro_mod", "vyro_mod256"],
    "division": ["vyro_div", "div256"],
    "exponentiation": ["pow", "pow"],
    "bitwise and": ["bitwise_and", "uint256_and"],
    "bitwise or": ["bitwise_or", "uint256_or"],
    "bitwise xor": ["bitwise_xor", "uint256_xor"],
}

COMPARE_TABLE = {
    "equality": ["vyro_eq", "uint256_eq"],
    "non-equality": ["vyro_neq", "neq256"],
    "less than": ["vyro_lt", "uint256_lt"],
    "less-or-equal": ["is_le_felt", "uint256_le"],
    "greater than": ["vyro_gt", "gt256"],
    "greater-or-equal": ["vyro_ge", "ge256"],
}

# Note: Vyper only supports `bitwise_not` for uint256
UNARY_OP_TABLE = {"bitwise not": ["bitwise_not", "uint256_not"]}


class OpsConverterVisitor(BaseVisitor):
    """
    Handles arithmetic, bitwise and boolean operations that require a Cairo builtin,
    and AugAssign nodes.
    """

    def visit_AugAssign(self, node: vy_ast.AugAssign, ast: vy_ast.Module, context: ASTContext):
        # Replace AugAssign with Assign
        target = node.target
        op = node.op
        value = node.value

        cairo_typ = convert_node_type_definition(node)

        if isinstance(target, vy_ast.Name):
            binop = vy_ast.BinOp(
                node_id=context.reserve_id(), left=target, op=op, right=value, ast_type="BinOp"
            )
            set_parent(value, binop)
            set_parent(target, binop)
            set_parent(op, binop)

            # Set to Vyper type for `uint256_handler` pass
            binop._metadata["type"] = cairo_typ

            target_copy = create_name_node(context, name=target.id)
            target_copy._metadata["type"] = cairo_typ

            ann_assign = vy_ast.AnnAssign(
                node_id=context.reserve_id(), target=target_copy, value=binop, ast_type="AnnAssign"
            )
            set_parent(binop, ann_assign)
            set_parent(target_copy, ann_assign)
            ann_assign._metadata["type"] = cairo_typ

            # Replace `AugAssign` node with `AnnAssign`
            ast.replace_in_tree(node, ann_assign)

    def visit_BinOp(self, node: vy_ast.BinOp, ast: vy_ast.Module, context: ASTContext):

        # Convert nested `BinOp` nodes first
        super().visit_BinOp(node, ast, context)

        cairo_typ = convert_node_type_definition(node)

        op = node.op
        op_description = node.op._description

        # Early termination if not in conversion table
        if op_description not in BINOP_TABLE:
            return

        is_uint256 = isinstance(cairo_typ, CairoUint256Definition)

        # Derive the operation
        vyro_op = BINOP_TABLE[op_description][1] if is_uint256 else BINOP_TABLE[op_description][0]

        if isinstance(op, vy_ast.Pow) and is_uint256:
            # Convert LHS and RHS to felt
            temp_left = create_name_node(context)
            temp_right = create_name_node(context)

            temp_left._metadata["type"] = FeltDefinition()
            temp_right._metadata["type"] = FeltDefinition()

            wrapped_left = create_call_node(context, "uint256_to_felt", args=[node.left])
            wrapped_left._metadata["type"] = FeltDefinition()

            wrapped_right = create_call_node(context, "uint256_to_felt", args=[node.right])
            wrapped_right._metadata["type"] = FeltDefinition()

            add_builtin_to_module(ast, "uint256_to_felt")

            left_conversion = create_assign_node(context, [temp_left], wrapped_left)
            right_conversion = create_assign_node(context, [temp_right], wrapped_right)

            # Duplicate temp LHS and RHS nodes
            temp_left_dup = create_name_node(context, name=temp_left.id)
            temp_right_dup = create_name_node(context, name=temp_right.id)

            temp_left_dup._metadata["type"] = FeltDefinition()
            temp_right_dup._metadata["type"] = FeltDefinition()

            # Exponentiate
            wrapped_op = create_call_node(context, vyro_op, args=[temp_left_dup, temp_right_dup])
            wrapped_op._metadata["type"] = FeltDefinition()

            convert_ret_node = create_name_node(context)
            convert_ret_node._metadata["type"] = FeltDefinition()

            convert_assign_node = create_assign_node(context, [convert_ret_node], wrapped_op)

            # Add import
            add_builtin_to_module(ast, vyro_op)

            # Convert back to Uint256
            reconvert_arg_node = create_name_node(context, name=convert_ret_node.id)
            reconvert_arg_node._metadata["type"] = FeltDefinition()

            wrapped_op = create_call_node(context, "felt_to_uint256", args=[reconvert_arg_node])
            wrapped_op._metadata["type"] = CairoUint256Definition()

            add_builtin_to_module(ast, "felt_to_uint256")

            reconvert_target_node = create_name_node(context)
            reconvert_target_node._metadata["type"] = CairoUint256Definition()

            reconvert_node = create_assign_node(context, [reconvert_target_node], wrapped_op)

            # Insert statements
            stmt_node = get_stmt_node(node)
            scope_node, scope_node_body = get_scope(node)
            insert_statement_before(reconvert_node, stmt_node, scope_node, scope_node_body)
            insert_statement_before(
                convert_assign_node, reconvert_node, scope_node, scope_node_body
            )
            insert_statement_before(
                right_conversion, convert_assign_node, scope_node, scope_node_body
            )
            insert_statement_before(
                left_conversion, convert_assign_node, scope_node, scope_node_body
            )

            # Replace `BinOp` with reconverted node
            replacement_node = create_name_node(context, name=reconvert_target_node.id)
            ast.replace_in_tree(node, replacement_node)
            return

        # Add implicits for bitwise ops
        if isinstance(op, (vy_ast.BitAnd, vy_ast.BitOr, vy_ast.BitXor)):
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap operation in a function call
        wrapped_op = create_call_node(context, vyro_op, args=[node.left, node.right])
        wrapped_op._metadata["type"] = cairo_typ

        # Assign to new variable
        temp_name_node = create_name_node(context)
        temp_name_node._metadata["type"] = cairo_typ

        temp_assign_node = create_assign_node(context, [temp_name_node], wrapped_op)

        stmt_node = get_stmt_node(node)
        scope_node, scope_node_body = get_scope(node)
        insert_statement_before(temp_assign_node, stmt_node, scope_node, scope_node_body)

        # Replace `BinOp` node with wrapped call reference
        temp_name_node_dup = create_name_node(context, name=temp_name_node.id)
        ast.replace_in_tree(node, temp_name_node_dup)

        # Add import
        add_builtin_to_module(ast, vyro_op)

    def visit_BoolOp(self, node: vy_ast.BoolOp, ast: vy_ast.Module, context: ASTContext):
        # Convert nested `BoolOp` nodes first
        super().visit_BoolOp(node, ast, context)

        # Assign felt type directly
        cairo_typ = FeltDefinition()

        if isinstance(node.op, vy_ast.And):
            vyro_op = "bitwise_and"
        elif isinstance(node.op, vy_ast.Or):
            vyro_op = "bitwise_or"

        add_implicit_to_function(node, "bitwise_ptr")
        add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap operation in a function call
        wrapped_op = create_call_node(context, vyro_op, args=node.values)
        wrapped_op._metadata["type"] = cairo_typ

        # Replace `BoolOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)

    def visit_Compare(self, node: vy_ast.Compare, ast: vy_ast.Module, context: ASTContext):
        # Convert nested `Compare` nodes first
        super().visit_Compare(node, ast, context)

        op = node.op

        if isinstance(op, (vy_ast.In, vy_ast.NotIn)):
            raise UnsupportedOperation("Membership operations are not supported", node)

        op_description = node.op._description
        left = node.left
        right = node.right

        output_typ = FeltDefinition()

        typ = node.left._metadata.get("type") or node.right._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

        is_uint256 = isinstance(cairo_typ, CairoUint256Definition)

        # Assign `Compare` to a new name `Assign` node
        temp_name_node = create_name_node(context)
        temp_name_node._metadata["type"] = output_typ

        vyro_op = (
            COMPARE_TABLE[op_description][1] if is_uint256 else COMPARE_TABLE[op_description][0]
        )
        add_builtin_to_module(ast, vyro_op)

        # Wrap `Compare` operation in a `Call` node
        wrapped_call = create_call_node(context, vyro_op, args=[left, right])

        temp_assign_node = create_assign_node(context, [temp_name_node], wrapped_call)

        # Add wrapped operation before `Compare` node
        stmt_node = get_stmt_node(node)
        scope_node, scope_node_body = get_scope(node)
        insert_statement_before(temp_assign_node, stmt_node, scope_node, scope_node_body)

        # Replace `Compare` node with referenced `Name` node
        temp_name_node_dup = create_name_node(context, name=temp_name_node.id)
        temp_name_node_dup._metadata["type"] = output_typ

        ast.replace_in_tree(node, temp_name_node_dup)

    def visit_UnaryOp(self, node: vy_ast.UnaryOp, ast: vy_ast.Module, context: ASTContext):
        cairo_typ = convert_node_type_definition(node)

        op = node.op
        if isinstance(op, vy_ast.Not):
            raise UnsupportedOperation("`not` operations are not supported.", node.op)

        op_description = op._description

        # Early termination if not in conversion table
        if op_description not in UNARY_OP_TABLE:
            return

        is_uint256 = isinstance(cairo_typ, CairoUint256Definition)

        # Derive the operation
        vyro_op = (
            UNARY_OP_TABLE[op_description][1] if is_uint256 else UNARY_OP_TABLE[op_description][0]
        )

        # Add implicits for bitwise ops
        if isinstance(op, (vy_ast.Invert,)):
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap operation in a function call
        wrapped_op = create_call_node(context, vyro_op, args=[node.operand])
        wrapped_op._metadata["type"] = cairo_typ

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)
