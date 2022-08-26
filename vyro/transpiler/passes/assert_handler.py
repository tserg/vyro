from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.nodes import CairoAssert
from vyro.cairo.types import FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import generate_name_node, insert_statement_before
from vyro.transpiler.visitor import BaseVisitor


class AssertHandlerVisitor(BaseVisitor):
    def visit_Assert(self, node: vy_ast.Assert, ast: vy_ast.Module, context: ASTContext):
        # Assign `test` condition to the RHS of an `Assign` node, to be inserted
        # before the `with_attr` block.
        condition = node.test

        temp_name_node = generate_name_node(context.reserve_id())
        temp_name_node._metadata["type"] = FeltDefinition()

        assign_node = vy_ast.Assign(
            node_id=context.reserve_id(), targets=[temp_name_node], value=condition
        )
        assign_node._metadata["type"] = FeltDefinition()

        fn_node = node.get_ancestor(vy_ast.FunctionDef)
        insert_statement_before(assign_node, node, fn_node)

        # Generate a new `test` condition where we assert newly assigned name node is True
        temp_name_node_dup = generate_name_node(context.reserve_id(), name=temp_name_node.id)
        temp_name_node._metadata["type"] = FeltDefinition()

        # Generate nodes for `CairoAssert`

        cairo_assert_target = temp_name_node_dup
        cairo_assert_value = generate_name_node(context.reserve_id(), name="TRUE")
        add_builtin_to_module(ast, "TRUE")

        assert_node = CairoAssert(
            node_id=context.reserve_id(), targets=[cairo_assert_target], value=cairo_assert_value
        )

        node.test = assert_node

    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):

        asserts = node.get_descendants(vy_ast.Assert)

        for a in asserts:
            self.visit(a, ast, context)
