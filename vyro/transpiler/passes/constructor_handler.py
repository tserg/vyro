from vyper import ast as vy_ast

from vyro.cairo.types import FeltDefinition
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import generate_name_node, get_cairo_type, set_parent
from vyro.transpiler.visitor import BaseVisitor


class ConstructorHandler(BaseVisitor):
    def visit_FunctionDef(self, node: vy_ast.FunctionDef, ast: vy_ast.Module, context: ASTContext):
        fn_typ = node._metadata.get("type")

        # Early termination if function is not constructor
        if not fn_typ.is_constructor:
            return

        # Change `__init__` to `constructor`
        node.name = "constructor"

        # Filter for immutable declarations and visit
        assign_children = [
            n for n in node.get_descendants(vy_ast.Assign) if isinstance(n.target, vy_ast.Name)
        ]

        for c in assign_children:
            self.visit(c, ast, context)

    def visit_Assign(self, node: vy_ast.Assign, ast: vy_ast.Module, context: ASTContext):
        # Check if it is an immutable
        varname = node.target.id
        is_immutable = ast.get_descendants(
            vy_ast.VariableDecl, {"is_immutable": True, "target.id": varname}
        )

        if len(is_immutable) == 0:
            return

        # Get type
        var_decl = is_immutable.pop()
        vy_typ = var_decl._metadata["type"]
        cairo_typ = get_cairo_type(vy_typ)

        # Update type of immutable declaration
        var_decl._metadata["type"] = cairo_typ

        # Transform LHS of assignment to immutable variable into `self.varname`
        node._children.remove(node.target)

        self_node = generate_name_node(context, name="self")
        self_node._metadata["type"] = FeltDefinition()

        attribute_node = vy_ast.Attribute(
            node_id=context.reserve_id(), attr=varname, value=self_node, ast_type="Attribute"
        )
        attribute_node._metadata["type"] = cairo_typ

        set_parent(self_node, attribute_node)

        node.target = attribute_node
        set_parent(attribute_node, node)

        # Replace subsequent references of immutable variable with `self.varname`
        # to make use of the storage var pass to read from storage

        contract_fns = ast.get_descendants(vy_ast.FunctionDef)

        for fn in contract_fns:
            fn_typ = fn._metadata.get("type")

            # Skip constructor because it has been handled
            if fn_typ.is_constructor:
                continue

            immutable_references = fn.get_descendants(vy_ast.Name, {"id": varname})

            for i in immutable_references:
                self_node = generate_name_node(context, name="self")
                self_node._metadata["type"] = FeltDefinition()

                attribute_node = vy_ast.Attribute(
                    node_id=context.reserve_id(),
                    attr=varname,
                    value=self_node,
                    ast_type="Attribute",
                )
                attribute_node._metadata["type"] = cairo_typ

                set_parent(self_node, attribute_node)

                ast.replace_in_tree(i, attribute_node)
