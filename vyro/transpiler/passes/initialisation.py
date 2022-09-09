from vyper import ast as vy_ast

from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    create_assign_node,
    generate_name_node,
    get_cairo_type,
    get_scope,
    initialise_function_implicits,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class InitialisationVisitor(BaseVisitor):
    def visit_AnnAssign(self, node: vy_ast.AnnAssign, ast: vy_ast.Module, context: ASTContext):
        # Move RHS into a local variable.
        # Since `AnnAssign` is a `tempvar`, it cannot be assigned to a function call.
        # Therefore, we re-assign the RHS to a temporary local variable.
        temp_name_node = generate_name_node(context)

        rhs = node.value
        node._children.remove(node.value)

        temp_assign_node = create_assign_node(context, [temp_name_node], rhs)

        # Insert `Assign` before `AnnAssign`
        scope_node, scope_body = get_scope(node)
        insert_statement_before(temp_assign_node, node, scope_node, scope_body)

        # Replace RHS with temp name node
        temp_name_node_dup = generate_name_node(context, name=temp_name_node.id)
        node.value = temp_name_node_dup
        set_parent(temp_name_node_dup, node)

        typ = node.target._metadata.get("type") or node._metadata.get("type")
        if typ:
            cairo_typ = get_cairo_type(typ)
            node._metadata["type"] = cairo_typ
            temp_assign_node._metadata["type"] = cairo_typ
            temp_name_node._metadata["type"] = cairo_typ
            temp_name_node_dup._metadata["type"] = cairo_typ

    def visit_AugAssign(self, node: vy_ast.AnnAssign, ast: vy_ast.Module, context: ASTContext):
        typ = node.target._metadata.get("type")
        cairo_typ = get_cairo_type(typ)
        node._metadata["type"] = cairo_typ

    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):
        # Initialise implicits
        initialise_function_implicits(node)

        to_visit = node.get_descendants((vy_ast.AnnAssign, vy_ast.AugAssign))

        for i in to_visit:
            self.visit(i, ast, context)

    def visit_Module(self, node: vy_ast.Module, ast: vy_ast.Module, context: ASTContext):
        # Initialise import directives
        node._metadata["import_directives"] = {}

        # Remove `implements`
        implements = ast.get_children(vy_ast.AnnAssign, {"target.id": "implements"})
        for i in implements:
            ast.remove_from_body(i)

        # Remove `vy_ast.ImportFrom`
        import_froms = ast.get_children(vy_ast.ImportFrom)
        for i in import_froms:
            ast.remove_from_body(i)

        for i in node.body:
            self.visit(i, ast, context)
