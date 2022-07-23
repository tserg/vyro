class VyroException(Exception):
    """
    Base exception class
    """

    def __init__(self, message="Error Message not found.", *items):
        """
        Exception initializer.

        Arguments
        ---------
        message : str
            Error message to display with the exception.
        *items : VyperNode | Tuple[str, VyperNode], optional
            Vyper ast node(s), or tuple of (description, node) indicating where
            the exception occured. Source annotations are generated in the order
            the nodes are given.

            A single tuple of (lineno, col_offset) is also understood to support
            the old API, but new exceptions should not use this approach.
        """
        self.message = message
        self.lineno = None
        self.col_offset = None
        self.annotations = items

    def __str__(self):

        if not hasattr(self, "annotations"):
            if self.lineno is not None and self.col_offset is not None:
                return f"line {self.lineno}:{self.col_offset} {self.message}"
            else:
                return self.message

        annotation_list = []
        annotation_msg = "\n".join(annotation_list)

        return f"{self.message}\n{annotation_msg}"


class UnsupportedNodeException(VyroException):
    """Unsupported Vyper AST node"""


class TranspilerPanic(VyroException):
    """Generic unexpected error during compilation"""
