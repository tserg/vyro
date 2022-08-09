from vyper import ast as vy_ast
from vyper.semantics.types import Uint256Definition
from vyper.semantics.types.bases import DataLocation
from vyper.semantics.types.utils import get_type_from_annotation

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.utils import get_cairo_type, wrap_operation_in_call
from vyro.transpiler.visitor import BaseVisitor


UINT256_BINOP_TABLE = {
    "addition": "add256",
    "subtraction": "sub256",
    "multiplication": "mul256",
}


class Uint256HandlerVisitor(BaseVisitor):
    def _wrap_literal_as_uint256(self, node, ast, context):
        """
        Replace literal node with wrapped `Uint256` `Call` node.
        """
        if isinstance(node, vy_ast.Int):
            lo = node.value & ((1 << 128) - 1)
            hi = node.value >> 128

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
            wrapped_convert = wrap_operation_in_call(
                ast, context, "Uint256", keywords=keywords
            )

            ast.replace_in_tree(node, wrapped_convert)
            node._children.add(wrapped_convert)

            # Set type
            wrapped_convert._metadata["type"] = CairoUint256Definition()

            # Add import
            add_builtin_to_module(ast, "Uint256")
        return


    def _wrap_convert(self, node, ast, context):
        value_node = node.value

        if isinstance(value_node, vy_ast.Int):
            self._wrap_literal_as_uint256(value_node, ast, context)
            node.target._metadata["type"] = CairoUint256Definition()

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
        op_description = node.op._description
        if op_description not in UINT256_BINOP_TABLE:
            return

        typ = node._metadata.get("type")
        cairo_typ = get_cairo_type(typ)

        # Early termination if `BinOp` is not of Uint256 type
        if not isinstance(cairo_typ, CairoUint256Definition):
            return

        # Determine the operation
        uint256_op = UINT256_BINOP_TABLE[op_description]

        # Wrap left and right in Uint256 if necessary
        self._wrap_literal_as_uint256(node.left, ast, context)
        self._wrap_literal_as_uint256(node.right, ast, context)

        # Wrap left and right in a function call
        wrapped_uint256_op = wrap_operation_in_call(
            ast, context, uint256_op, args=[node.left, node.right]
        )
        wrapped_uint256_op._metadata["type"] = cairo_typ

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_uint256_op)

        # Add import
        add_builtin_to_module(ast, uint256_op)
