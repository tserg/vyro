import json

from vyro.utils.docopt import docopt
from vyro.vyper.vyper_compile import get_vyper_ast

__doc__ = """Usage: vyro transform [<contract>]

Arguments
  [<contract>]          Name of Vyper contract to compile.

Prints the Vyper AST to console
"""


def main():
    args = docopt(__doc__)

    if args["<contract>"]:
        path = args["<contract>"]

        # Get Vyper AST
        vyper_ast = get_vyper_ast(path)
        ast_dict = vyper_ast.to_dict()
        print(json.dumps(ast_dict, indent=4, sort_keys=True))
