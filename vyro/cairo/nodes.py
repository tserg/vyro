from typing import Optional

from vyper import ast as vy_ast


class CairoAssert(vy_ast.Assign):
    """Wrapper class for Cairo assert"""

    def __init__(self, parent: Optional[vy_ast.VyperNode] = None, **kwargs: dict):
        self.ast_type = "CairoAssert"
        super().__init__(parent, **kwargs)


class CairoIfTest(vy_ast.Compare):
    """Wrapper class for test condition of Cairo's `if`"""

    def __init__(self, parent: Optional[vy_ast.VyperNode] = None, **kwargs: dict):
        self.ast_type = "CairoIfTest"
        super().__init__(parent, **kwargs)


class CairoStorageWrite(vy_ast.Assign):
    """Wrapper class for Cairo write to storage"""

    def __init__(self, parent: Optional[vy_ast.VyperNode] = None, **kwargs: dict):
        self.ast_type = "CairoStorageWrite"
        super().__init__(parent, **kwargs)


class CairoStorageRead(vy_ast.Assign):
    """Wrapper class for Cairo read from storage"""

    args = []

    def __init__(self, parent: Optional[vy_ast.VyperNode] = None, **kwargs: dict):
        self.ast_type = "CairoStorageRead"
        super().__init__(parent, **kwargs)

        if kwargs.get("args"):
            self.args = kwargs["args"]
