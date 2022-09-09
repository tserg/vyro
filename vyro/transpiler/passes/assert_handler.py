from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.nodes import CairoAssert
from vyro.cairo.types import FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    create_assign_node,
    create_name_node,
    get_scope,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class AssertHandlerVisitor(BaseVisitor):
    def visit_Assert(self, node: vy_ast.Assert, ast: vy_ast.Module, context: ASTContext):
        # Assign `test` condition to the RHS of an `Assign` node, to be inserted
        # before the `with_attr` block.
        condition = node.test
        node._children.remove(condition)

        temp_name_node = create_name_node(context)
        temp_name_node._metadata["type"] = FeltDefinition()

        assign_node = create_assign_node(context, [temp_name_node], condition)
        assign_node._metadata["type"] = FeltDefinition()

        scope_node, scope_node_body = get_scope(node)
        insert_statement_before(assign_node, node, scope_node, scope_node_body)

        # Generate a new `test` condition where we assert newly assigned name node is True
        cairo_assert_target = create_name_node(context, name=temp_name_node.id)
        temp_name_node._metadata["type"] = FeltDefinition()

        # Generate nodes for `CairoAssert`

        cairo_assert_value = create_name_node(context, name="TRUE")
        add_builtin_to_module(ast, "TRUE")

        assert_node = CairoAssert(
            node_id=context.reserve_id(), targets=[cairo_assert_target], value=cairo_assert_value
        )
        set_parent(cairo_assert_target, assert_node)
        set_parent(cairo_assert_value, assert_node)

        node.test = assert_node
        set_parent(assert_node, node)

    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):

        asserts = node.get_descendants(vy_ast.Assert)

        for a in asserts:
            self.visit(a, ast, context)
