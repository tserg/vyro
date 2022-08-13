from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, FeltDefinition
from vyro.exceptions import UnsupportedOperation
from vyro.transpiler.utils import (
    add_implicit_to_function,
    generate_name_node,
    get_cairo_type,
    set_parent,
    wrap_operation_in_call,
)
from vyro.transpiler.visitor import BaseVisitor

BINOP_TABLE = {
    # operation: [felt op, uint256 op]
    "modulus": ["vyro_mod", "vyro_mod256"],
    "division": ["vyro_div", "div256"],
    "exponentiation": ["pow", None],
    "bitwise and": ["bitwise_and", "uint256_and"],
    "bitwise or": ["bitwise_or", "uint256_or"],
    "bitwise xor": ["bitwise_xor", "uint256_xor"],
}

# Note: Vyper only supports `bitwise_not` for uint256
UNARY_OP_TABLE = {"bitwise not": ["bitwise_not", "uint256_not"]}


class OpsConverterVisitor(BaseVisitor):
    """
    Handles arithmetic, bitwise and boolean operations that require a Cairo builtin,
    and AugAssign nodes.
    """

    def visit_AugAssign(self, node, ast, context):
        # Replace AugAssign with Assign
        target = node.target
        op = node.op
        value = node.value

        typ = node._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

        binop = vy_ast.BinOp(
            node_id=context.reserve_id(),
            left=target,
            op=op,
            right=value,
            ast_type="BinOp",
        )
        binop._children.add(target)
        binop._children.add(op)
        binop._children.add(value)
        set_parent(value, binop)
        set_parent(target, binop)
        set_parent(op, binop)

        # Set to Vyper type for `uint256_handler` pass
        binop._metadata["type"] = cairo_typ

        target_copy = generate_name_node(context.reserve_id(), name=target.id)
        target_copy._metadata["type"] = cairo_typ

        ann_assign = vy_ast.AnnAssign(
            node_id=context.reserve_id(),
            target=target_copy,
            value=binop,
            ast_type="AnnAssign",
        )
        ann_assign._children.add(target_copy)
        ann_assign._children.add(binop)
        set_parent(binop, ann_assign)
        set_parent(target_copy, ann_assign)
        ann_assign._metadata["type"] = cairo_typ

        # Replace `AugAssign` node with `AnnAssign`
        ast.replace_in_tree(node, ann_assign)

    def visit_BinOp(self, node, ast, context):
        typ = node._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

        op = node.op
        op_description = node.op._description

        # Early termination if not in conversion table
        if op_description not in BINOP_TABLE:
            return

        is_uint256 = isinstance(cairo_typ, CairoUint256Definition)
        if isinstance(op, vy_ast.Pow) and is_uint256:
            raise UnsupportedOperation(
                "`pow` operations for Uint256 are not supported.", node
            )

        # Derive the operation
        vyro_op = (
            BINOP_TABLE[op_description][1]
            if is_uint256
            else BINOP_TABLE[op_description][0]
        )

        # Add implicits for bitwise ops
        if isinstance(op, (vy_ast.BitAnd, vy_ast.BitOr, vy_ast.BitXor)):
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap operation in a function call
        wrapped_op = wrap_operation_in_call(
            ast, context, vyro_op, [node.left, node.right]
        )
        wrapped_op._metadata["type"] = cairo_typ

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)

    def visit_BoolOp(self, node, ast, context):
        # Assign felt type directly
        cairo_typ = FeltDefinition()

        if isinstance(node.op, vy_ast.And):
            vyro_op = "bitwise_and"
        elif isinstance(node.op, vy_ast.Or):
            vyro_op = "bitwise_or"

        add_implicit_to_function(node, "bitwise_ptr")
        add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap operation in a function call
        wrapped_op = wrap_operation_in_call(ast, context, vyro_op, node.values)
        wrapped_op._metadata["type"] = cairo_typ

        # Replace `BoolOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)

    def visit_UnaryOp(self, node, ast, context):
        typ = node._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

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
            UNARY_OP_TABLE[op_description][1]
            if is_uint256
            else UNARY_OP_TABLE[op_description][0]
        )

        # Add implicits for bitwise ops
        if isinstance(op, (vy_ast.Invert,)):
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap operation in a function call
        wrapped_op = wrap_operation_in_call(ast, context, vyro_op, [node.operand])
        wrapped_op._metadata["type"] = cairo_typ

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)
