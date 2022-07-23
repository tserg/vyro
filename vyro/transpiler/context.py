from vyper import ast as vy_ast


class ASTContext:
    def __init__(self):
        self.last_id = 0

    @classmethod
    def get_context(cls, vyper_module: vy_ast.Module) -> "ASTContext":
        ctx = cls()

        # Get the last node
        last_child = vyper_module.get_descendants(reverse=False).pop()
        ctx.last_id = last_child.node_id
        return ctx

    def reserve_id(self):
        self.last_id += 1
        return self.last_id
