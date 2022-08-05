class VyroException(Exception):
    """
    Base exception class
    """

    def __init__(self, message="Error Message not found.", node=None):
        """
        Exception initializer.

        Arguments
        ---------
        message : str
            Error message to display with the exception.
        *items : VyperNode
            Vyper ast node(s) indicating where the exception occured.
            Source annotations are generated in the order the nodes are given.
        """
        self.message = message

    def __str__(self):
        return f"\nTranspilation failed with the following error:\n{self.message}\n"


class UnsupportedNode(VyroException):
    """Unsupported Vyper AST node"""


class UnsupportedType(VyroException):
    """Unsupported Vyper type"""


class TranspilerPanic(VyroException):
    """Generic unexpected error during compilation"""
