import json

from vyro.cairo.writer import write
from vyro.transpiler.transpile import transpile
from vyro.utils.docopt import docopt
from vyro.utils.output import write_cairo
from vyro.vyper.vyper_compile import get_vyper_ast

__doc__ = """Usage: vyro transpile [<contract>] [options]

Arguments
  [<contract>]          Name of Vyper contract to compile.

Options:
  --help -h             Display this message.
  --output <file>       Write the transpiled Cairo to a file.
  --print-output        Print the transpiled Cairo to console.
  --print-tree          Print the transpiled AST to console.

Transpiles the contract source file
"""


def main():
    args = docopt(__doc__)

    if args["<contract>"]:
        path = args["<contract>"]
        print_tree = args["--print-tree"]
        print_output = args["--print-output"]

        # Get Vyper AST
        vyper_ast = get_vyper_ast(path)

        # Transpile
        transpile(vyper_ast, print_tree=print_tree)

        # Get transpiled Cairo in str format
        output = write(vyper_ast)

        # Write to output file
        output_file = args["--output"]
        if output_file:
            write_cairo(output, output_file)

        # Print Cairo output to console
        if print_output:
            print(output)

        if print_tree:
            ast_dict = vyper_ast.to_dict()
            print("\n\n=============== Transpiled AST ===============\n\n")
            print(json.dumps(ast_dict, sort_keys=True, indent=4))

        print(f"\nSuccessfully transpiled {path}!")
