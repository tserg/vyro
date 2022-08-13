from vyro.transpiler.visitor import BaseVisitor


class ConstructorHandler(BaseVisitor):
    def visit_FunctionDef(self, node, ast, context):
        fn_typ = node._metadata.get("type")

        # Early termination if function is not constructor
        if not fn_typ.is_constructor:
            return

        # Change `__init__` to `constructor`
        node.name = "constructor"
