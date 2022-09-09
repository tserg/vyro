from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.nodes import CairoIfTest
from vyro.cairo.types import FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    create_assign_node,
    generate_name_node,
    get_scope,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class IfHandlerVisitor(BaseVisitor):
    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):
        # Extract `If` nodes to prevent infinite loop
        if_nodes = node.get_descendants(vy_ast.If)
        for if_node in if_nodes:
            self.visit_If(if_node, ast, context)

    def visit_If(self, node: vy_ast.If, ast: vy_ast.Module, context: ASTContext):

        # Assign test condition to a temporary variable in an `Assign` statement
        # before `If` node
        condition = node.test
        node._children.remove(node.test)

        temp_name_node = generate_name_node(context.reserve_id())
        temp_name_node._metadata["type"] = FeltDefinition()

        assign_condition_node = create_assign_node(
            context,
            [temp_name_node],
            condition,
        )

        scope_node, scope_node_body = get_scope(node)
        insert_statement_before(assign_condition_node, node, scope_node, scope_node_body)

        # Replace 'test' for `If` node with `CairoIfTest` of temporary variable to TRUE
        temp_name_node_dup = generate_name_node(context.reserve_id(), name=temp_name_node.id)
        temp_name_node_dup._metadata["type"] = FeltDefinition()

        true_constant_node = generate_name_node(context.reserve_id(), name="TRUE")
        true_constant_node._metadata["type"] = FeltDefinition()
        add_builtin_to_module(ast, "TRUE")

        compare_node = CairoIfTest(
            node_id=context.reserve_id(),
            ops=[vy_ast.Eq()],
            left=temp_name_node_dup,
            comparators=[true_constant_node],
            ast_type="Compare",
        )
        set_parent(temp_name_node_dup, compare_node)
        set_parent(true_constant_node, compare_node)

        node.test = compare_node
        set_parent(compare_node, node)
