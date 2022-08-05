from vyper import ast as vy_ast
from vyper.semantics.types import Uint256Definition
from vyper.semantics.types.bases import DataLocation
from vyper.semantics.types.utils import get_type_from_annotation

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition, get_cairo_type
from vyro.transpiler.visitor import BaseVisitor


class Uint256HandlerVisitor(BaseVisitor):
    def _wrap_convert(self, node, ast, context):
        value_node = node.value

        if isinstance(value_node, vy_ast.Int):

            lo = value_node.value & ((1 << 128) - 1)
            hi = value_node.value >> 128

            # Cast literals as Uint256
            wrapped_convert = vy_ast.Call(
                node_id=context.reserve_id(),
                func=vy_ast.Name(
                    node_id=context.reserve_id(), id="Uint256", ast_type="Name"
                ),
                args=vy_ast.arguments(
                    node_id=context.reserve_id(), args=[], ast_type="arguments"
                ),
                keywords=[
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
                ],
            )

            node.value = wrapped_convert
            node._children.add(wrapped_convert)

            # Set type
            node.target._metadata["type"] = CairoUint256Definition()
            node.value._metadata["type"] = CairoUint256Definition()

            # Add import
            add_builtin_to_module(ast, "Uint256")

        elif isinstance(value_node, vy_ast.Name):
            value_typ = value_node._metadata["type"]
            if isinstance(value_typ, Uint256Definition):
                # Set type
                node.target._metadata["type"] = CairoUint256Definition()
                node.value._metadata["type"] = CairoUint256Definition()

        return

    def visit_arg(self, node, ast, context):
        vyper_typ = get_type_from_annotation(node.annotation, DataLocation.UNSET)
        cairo_typ = get_cairo_type(vyper_typ)
        node._metadata["type"] = cairo_typ

    def visit_AnnAssign(self, node, ast, context):
        type_ = node.value._metadata.get("type")
        if isinstance(type_, Uint256Definition):
            self._wrap_convert(node, ast, context)

    def visit_Assign(self, node, ast, context):
        type_ = node.value._metadata.get("type")
        if isinstance(type_, Uint256Definition):
            self._wrap_convert(node, ast, context)

        self.visit(node.value, ast, context)

    def visit_BinOp(self, node, ast, context):
        typ = node._metadata.get("type")

        # Early termination if `BinOp` is not of Uint256 type
        if not isinstance(typ, Uint256Definition):
            return

        op = node.op

        # Determine the operation
        if isinstance(op, vy_ast.Add):
            uint256_op = "add256"
        elif isinstance(op, vy_ast.Sub):
            uint256_op = "sub256"
        elif isinstance(op, vy_ast.Mult):
            uint256_op = "mul256"
        elif isinstance(op, vy_ast.Div):
            uint256_op = "div256"
        else:
            return

        # Wrap left and right in a function call
        wrapped_uint256_op = vy_ast.Call(
            node_id=context.reserve_id(),
            func=vy_ast.Name(
                node_id=context.reserve_id(), id=uint256_op, ast_type="Name"
            ),
            args=vy_ast.arguments(
                node_id=context.reserve_id(),
                args=[node.left, node.right],
                ast_type="arguments",
            ),
            keywords=[],
        )

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_uint256_op)

        # Add import
        add_builtin_to_module(ast, uint256_op)
