from vyper import ast as vy_ast
from vyper.semantics.types import Uint256Definition

from vyro.cairo.import_directives import add_builtin_to_module
from vyro.transpiler.visitor import BaseVisitor
from vyro.transpiler.utils import generate_name_node, insert_statement_before


class Uint256HandlerVisitor(BaseVisitor):
    def _wrap_convert(self, node, ast, context):
        value_node = node.value

        if isinstance(value_node, vy_ast.Int):

            lo = value_node.value & ((1 << 128) - 1)
            hi = value_node.value >> 128

            # Wrap value in a `felt_to_uint256` call
            wrapped_convert = vy_ast.Call(
                node_id=context.reserve_id(),
                func=vy_ast.Name(
                    node_id=context.reserve_id(),
                    id="Uint256",
                ),
                args=vy_ast.arguments(
                    node_id=context.reserve_id(),
                    args=[],
                ),
                keywords=[
                    vy_ast.keyword(
                        node_id=context.reserve_id(),
                        arg="low",
                        value=vy_ast.Int(
                            node_id=context.reserve_id(),
                            value=lo,
                        ),
                    ),
                    vy_ast.keyword(
                        node_id=context.reserve_id(),
                        arg="high",
                        value=vy_ast.Int(
                            node_id=context.reserve_id(),
                            value=hi,
                        ),
                    ),
                ],
            )

            node.value = wrapped_convert
            node._children.add(wrapped_convert)

            # Add import
            add_builtin_to_module(ast, "Uint256")

        else:
            # Wrap value in a `felt_to_uint256` call
            wrapped_convert = vy_ast.Call(
                node_id=context.reserve_id(),
                func=vy_ast.Name(
                    node_id=context.reserve_id(),
                    id="felt_to_uint256",
                ),
                args=vy_ast.arguments(
                    node_id=context.reserve_id(),
                    args=[],
                    defaults=[],
                ),
                keywords=[],
            )

            ast.replace_in_tree(node.value, wrapped_convert)
            wrapped_convert.args.args.append(value_node)

            # Add import
            add_builtin_to_module(ast, "felt_to_uint256")
            add_builtin_to_module(ast, "Uint256")

        return


    def visit_AnnAssign(self, node, ast, context):
        type_ = node.value._metadata.get("type")
        if isinstance(type_, Uint256Definition):
            self._wrap_convert(node, ast, context)

    def visit_Assign(self, node, ast, context):
        type_ = node.value._metadata.get("type")
        if isinstance(type_, Uint256Definition):
            self._wrap_convert(node, ast, context)
