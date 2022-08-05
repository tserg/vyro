from typing import Optional

from vyper import ast as vy_ast


class CairoStorageWrite(vy_ast.Assign):
    """Wrapper class for Cairo write to storage"""

    def __init__(self, parent: Optional[vy_ast.VyperNode] = None, **kwargs: dict):
        self.ast_type = "CairoStorageWrite"
        super().__init__(parent, **kwargs)


class CairoStorageRead(vy_ast.Assign):
    """Wrapper class for Cairo read from storage"""

    def __init__(self, parent: Optional[vy_ast.VyperNode] = None, **kwargs: dict):
        self.ast_type = "CairoStorageRead"
        super().__init__(parent, **kwargs)
