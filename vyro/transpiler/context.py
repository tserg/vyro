from vyper import ast as vy_ast


def _get_largest_node_id(d: dict):
    """
    Walks the AST dict to get the largest `node_id`.
    """
    for k, v in d.items():
        if k == "node_id":
            yield v
        elif isinstance(v, dict):
            for i in _get_largest_node_id(v):
                yield i
        elif isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    for j in _get_largest_node_id(i):
                        yield j

class ASTContext:
    def __init__(self):
        self.last_id = 0

    @classmethod
    def get_context(cls, vyper_module: vy_ast.Module) -> "ASTContext":
        ctx = cls()

        ast_dict = vyper_module.to_dict()

        largest = 0
        for node_id in _get_largest_node_id(ast_dict):
            if node_id > largest:
                largest = node_id

        ctx.last_id = largest
        return ctx

    def reserve_id(self):
        self.last_id += 1
        return self.last_id
