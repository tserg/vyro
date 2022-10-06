from vyper import ast as vy_ast
from vyper.semantics.types.user.struct import StructPrimitive
from vyper.semantics.validation.utils import get_exact_type_from_node

from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import set_parent
from vyro.transpiler.visitor import BaseVisitor


class StructConverterVisitor(BaseVisitor):
    def visit_Assign(self, node: vy_ast.Assign, ast: vy_ast.Module, context: ASTContext):
        value_node = node.value
        if isinstance(value_node, vy_ast.Call):
            call_typ = get_exact_type_from_node(value_node.func)
            if not isinstance(call_typ, StructPrimitive):
                return

            # Unwrap `vy_ast.Dict` node for members into individual `vy_ast.keywords` node
            args_dict_node = value_node.args[0]
            value_node.args = []
            value_node._children.remove(args_dict_node)

            for name_node, v in zip(args_dict_node.keys, args_dict_node.values):
                kw_node = vy_ast.keyword(
                    node_id=context.reserve_id(),
                    arg=name_node.id,
                    value=v,
                    ast_type="keyword",
                )
                value_node.keywords.append(kw_node)
                set_parent(v, kw_node)
                set_parent(kw_node, value_node)
