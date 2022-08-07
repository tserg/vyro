from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.exceptions import UnsupportedOperation
from vyro.transpiler.utils import add_implicit_to_function, get_cairo_type
from vyro.transpiler.visitor import BaseVisitor


class BinOpConverterVisitor(BaseVisitor):
    def visit_BinOp(self, node, ast, context):
        typ = node._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

        op = node.op

        if isinstance(op, vy_ast.Mod):
            vyro_op = (
                "vyro_mod256"
                if isinstance(cairo_typ, CairoUint256Definition)
                else "vyro_mod"
            )
        elif isinstance(op, vy_ast.Div):
            vyro_op = (
                "div256"
                if isinstance(cairo_typ, CairoUint256Definition)
                else "vyro_div"
            )
        elif isinstance(op, vy_ast.Pow):
            if isinstance(cairo_typ, CairoUint256Definition):
                raise UnsupportedOperation(
                    "`pow` operations for Uint256 are not supported.", node
                )
            vyro_op = "pow"
        elif isinstance(op, vy_ast.BitAnd):
            vyro_op = (
                "uint256_and"
                if isinstance(cairo_typ, CairoUint256Definition)
                else "bitwise_and"
            )
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")
        elif isinstance(op, vy_ast.BitOr):
            vyro_op = (
                "uint256_or"
                if isinstance(cairo_typ, CairoUint256Definition)
                else "bitwise_or"
            )
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")
        elif isinstance(op, vy_ast.BitXor):
            vyro_op = (
                "uint256_xor"
                if isinstance(cairo_typ, CairoUint256Definition)
                else "bitwise_xor"
            )
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")
        else:
            return

        # Wrap left and right in a function call
        wrapped_op = vy_ast.Call(
            node_id=context.reserve_id(),
            func=vy_ast.Name(node_id=context.reserve_id(), id=vyro_op, ast_type="Name"),
            args=vy_ast.arguments(
                node_id=context.reserve_id(),
                args=[node.left, node.right],
                ast_type="arguments",
            ),
            keywords=[],
        )

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)

    def visit_BoolOp(self, node, ast, context):
        typ = node._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

        op = node.op

        if isinstance(op, vy_ast.And):
            vyro_op ="bitwise_and"
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")
        elif isinstance(op, vy_ast.Or):
            vyro_op = "bitwise_or"
            add_implicit_to_function(node, "bitwise_ptr")
            add_builtin_to_module(ast, "BitwiseBuiltin")

        # Wrap left and right in a function call
        values = node.values
        wrapped_op = vy_ast.Call(
            node_id=context.reserve_id(),
            func=vy_ast.Name(node_id=context.reserve_id(), id=vyro_op, ast_type="Name"),
            args=vy_ast.arguments(
                node_id=context.reserve_id(),
                args=[values[0], values[1]],
                ast_type="arguments",
            ),
            keywords=[],
        )

        # Replace `BoolOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_op)

        # Add import
        add_builtin_to_module(ast, vyro_op)
