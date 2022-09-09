from vyper import ast as vy_ast

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.cairo.types import FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    create_assign_node,
    create_call_node,
    generate_name_node,
    insert_statement_before,
)
from vyro.transpiler.visitor import BaseVisitor


class MsgSenderConverterVisitor(BaseVisitor):
    """
    Extract `msg.sender` into a call to `get_caller_address` as a preceding statement.
    """

    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):
        # Search for `msg.sender`
        nodes_to_replace = node.get_descendants(
            vy_ast.Attribute, {"attr": "sender", "value.id": "msg"}, reverse=True
        )

        # If found, create a new `Assign` statement to `get_caller_address`
        if len(nodes_to_replace) > 0:
            temp_name_node = generate_name_node(context.reserve_id())
            temp_name_node._metadata["type"] = FeltDefinition()

            syscall_node = create_call_node(context, "get_caller_address")
            syscall_node.func._metadata["type"] = FeltDefinition()

            wrapped_call = create_assign_node(context, [temp_name_node], syscall_node)
            wrapped_call._metadata["type"] = FeltDefinition()

            # Add builtin
            add_builtin_to_module(ast, "get_caller_address")

            # Insert the wrapped call into the head of the function node body
            first_statement = node.body[0]
            insert_statement_before(wrapped_call, first_statement, node, node.body)

            # Replace `msg.sender` with the temp reference
            temp_name_node_ref = temp_name_node.id
            temp_name_reference_node = generate_name_node(
                context.reserve_id(), name=temp_name_node_ref
            )

            first_call_node = nodes_to_replace.pop()
            ast.replace_in_tree(first_call_node, temp_name_node)

            # Replace all descendants of the FunctionDef node with the replace variable

            for n in nodes_to_replace:
                temp_name_reference_node = generate_name_node(
                    context.reserve_id(), name=temp_name_node_ref
                )
                ast.replace_in_tree(n, temp_name_reference_node)
