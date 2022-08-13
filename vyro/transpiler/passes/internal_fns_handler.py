from vyper import ast as vy_ast

from vyro.transpiler.utils import generate_name_node
from vyro.transpiler.visitor import BaseVisitor


class InternalFunctionsHandler(BaseVisitor):
    def visit_Call(self, node, ast, context):
        fn_typ = node.func._metadata["type"]

        fn_name = node.func.attr

        if fn_typ.is_internal:
            # Unwrap `foo` from `self.foo`
            fn_name_node = vy_ast.Name.from_node(
                node,
                id=fn_name,
            )
            fn_name_node._metadata["type"] = fn_typ

            # Replace `self.foo` with `foo`
            ast.replace_in_tree(node.func, fn_name_node)