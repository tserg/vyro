from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import CairoUint256Definition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    convert_node_type_definition,
    create_assign_node,
    create_call_node,
    create_name_node,
    get_cairo_type,
    get_scope,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor

UINT256_BINOP_TABLE = {"addition": "add256", "subtraction": "sub256", "multiplication": "mul256"}


class Uint256HandlerVisitor(BaseVisitor):
    def visit_AnnAssign(self, node: vy_ast.AnnAssign, ast: vy_ast.Module, context: ASTContext):
        type_ = node.value._metadata.get("type")

        if type_:
            cairo_typ = get_cairo_type(type_)
            node.target._metadata["type"] = cairo_typ
            node._metadata["type"] = cairo_typ

            if isinstance(node.value, vy_ast.BinOp) and isinstance(
                cairo_typ, CairoUint256Definition
            ):
                value_node = node.value

                temp_name_node = create_name_node(context)
                temp_name_node._metadata["type"] = cairo_typ

                rhs_assignment_node = create_assign_node(context, [temp_name_node], value_node)
                rhs_assignment_node._metadata["type"] = cairo_typ

                scope_node, scope_node_body = get_scope(node)
                insert_statement_before(rhs_assignment_node, node, scope_node, scope_node_body)

                # Replace `BinOp` with temporary name node
                temp_name_node_copy = create_name_node(context, name=temp_name_node.id)
                temp_name_node_copy._metadata["type"] = cairo_typ
                node.value = temp_name_node_copy

                # Visit newly added assignment node
                self.visit(rhs_assignment_node, ast, context)

        super().visit_AnnAssign(node, ast, context)

    def visit_Assign(self, node: vy_ast.Assign, ast: vy_ast.Module, context: ASTContext):
        type_ = node.value._metadata.get("type")

        if type_:
            cairo_typ = get_cairo_type(type_)
            node.target._metadata["type"] = cairo_typ
            node._metadata["type"] = cairo_typ

        super().visit_Assign(node, ast, context)

    def visit_BinOp(self, node: vy_ast.BinOp, ast: vy_ast.Module, context: ASTContext):
        op_description = node.op._description
        if op_description not in UINT256_BINOP_TABLE:
            return

        cairo_typ = convert_node_type_definition(node)

        # Early termination if `BinOp` is not of Uint256 type
        if not isinstance(cairo_typ, CairoUint256Definition):
            return

        # Determine the operation
        uint256_op = UINT256_BINOP_TABLE[op_description]

        left = node.left
        right = node.right

        # Wrap left and right in a function call
        wrapped_uint256_op = create_call_node(context, uint256_op, args=[left, right])
        set_parent(left, wrapped_uint256_op)
        set_parent(right, wrapped_uint256_op)
        wrapped_uint256_op._metadata["type"] = cairo_typ

        # Replace `BinOp` node with wrapped call
        ast.replace_in_tree(node, wrapped_uint256_op)

        # Add import
        add_builtin_to_module(ast, uint256_op)

        # Visit wrapped call node
        self.visit(wrapped_uint256_op, ast, context)

    def visit_Int(self, node: vy_ast.Int, ast: vy_ast.Module, context: ASTContext):
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
                        value=vy_ast.Int(node_id=context.reserve_id(), value=lo, ast_type="Int"),
                        ast_type="keyword",
                    ),
                    vy_ast.keyword(
                        node_id=context.reserve_id(),
                        arg="high",
                        value=vy_ast.Int(node_id=context.reserve_id(), value=hi, ast_type="Int"),
                        ast_typ="keyword",
                    ),
                ]
                wrapped_convert = create_call_node(context, "Uint256", keywords=keywords)

                # Replace node with wrapped convert
                ast.replace_in_tree(node, wrapped_convert)

                # Set type
                wrapped_convert._metadata["type"] = CairoUint256Definition()

                # Add import
                add_builtin_to_module(ast, "Uint256")

    def visit_Module(self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext):
        # Skip contract vars
        nodes = [i for i in node.body if not isinstance(i, vy_ast.VariableDecl)]
        for n in nodes:
            self.visit(n, ast, context)
