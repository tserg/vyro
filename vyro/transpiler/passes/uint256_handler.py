from vyper import ast as vy_ast
from vyper.semantics.types.bases import DataLocation
from vyper.semantics.types.utils import get_type_from_annotation

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.utils import (
    generate_name_node,
    get_cairo_type,
    insert_statement_before,
    set_parent,
    wrap_operation_in_call,
)
from vyro.transpiler.visitor import BaseVisitor

UINT256_BINOP_TABLE = {
    "addition": "add256",
    "subtraction": "sub256",
    "multiplication": "mul256",
}


class Uint256HandlerVisitor(BaseVisitor):
    def visit_arg(self, node, ast, context):
        vyper_typ = get_type_from_annotation(node.annotation, DataLocation.UNSET)
        cairo_typ = get_cairo_type(vyper_typ)
        node._metadata["type"] = cairo_typ

    def visit_AnnAssign(self, node, ast, context):
        type_ = node.value._metadata.get("type")

        if type_:
            cairo_typ = get_cairo_type(type_)
            node.target._metadata["type"] = cairo_typ
            node._metadata["type"] = cairo_typ

            if isinstance(node.value, vy_ast.BinOp) and isinstance(
                cairo_typ, CairoUint256Definition
            ):
                value_node = node.value

                temp_name_node = generate_name_node(context.reserve_id())
                temp_name_node._metadata["type"] = cairo_typ

                rhs_assignment_node = vy_ast.Assign(
                    node_id=context.reserve_id(),
                    targets=[temp_name_node],
                    value=value_node,
                    ast_type="Assign",
                )
                rhs_assignment_node._children.add(temp_name_node)
                rhs_assignment_node._children.add(value_node)
                rhs_assignment_node._metadata["type"] = cairo_typ
                set_parent(value_node, rhs_assignment_node)

                fn_node = node.get_ancestor(vy_ast.FunctionDef)
                insert_statement_before(rhs_assignment_node, node, fn_node)

                # Replace `BinOp` with temporary name node
                temp_name_node_copy = generate_name_node(
                    context.reserve_id(), name=temp_name_node.id
                )
                temp_name_node_copy._metadata["type"] = cairo_typ
                node.value = temp_name_node_copy

                # Visit newly added assignment node
                self.visit(rhs_assignment_node, ast, context)

        self.visit(node.value, ast, context)

    def visit_Assign(self, node, ast, context):
        type_ = node.value._metadata.get("type")

        if type_:
            cairo_typ = get_cairo_type(type_)
            node.target._metadata["type"] = cairo_typ
            node._metadata["type"] = cairo_typ

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

        left = node.left
        right = node.right

        # Wrap left and right in a function call
        wrapped_uint256_op = wrap_operation_in_call(
            ast, context, uint256_op, args=[left, right]
        )
        set_parent(left, wrapped_uint256_op)
        set_parent(right, wrapped_uint256_op)
        wrapped_uint256_op._children.add(left)
        wrapped_uint256_op._children.add(right)
        wrapped_uint256_op._metadata["type"] = cairo_typ

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_uint256_op)

        # Add import
        add_builtin_to_module(ast, uint256_op)

        # Visit wrapped call node
        self.visit(wrapped_uint256_op, ast, context)

    def visit_Int(self, node, ast, context):
        typ = node._metadata.get("type")
        if typ:
            cairo_typ = get_cairo_type(typ)
            if isinstance(cairo_typ, CairoUint256Definition):
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

                # Replace node with wrapped convert
                ast.replace_in_tree(node, wrapped_convert)

                # Set type
                wrapped_convert._metadata["type"] = CairoUint256Definition()

                # Add import
                add_builtin_to_module(ast, "Uint256")

    def visit_Module(self, node, ast, context):
        # Skip contract vars
        nodes = [i for i in node.body if not isinstance(i, vy_ast.VariableDecl)]
        for n in nodes:
            self.visit(n, ast, context)
