from vyro.cairo.writer import write
from vyro.transpiler.transpile import transpile
from vyro.utils.output import write_cairo
from vyro.vyper.vyper_compile import get_vyper_ast

CAIRO_PRIME = 2**251 + 17 * 2**192 + 1


def transpile_to_cairo(path, output_file):
    vyper_ast = get_vyper_ast(path)

    # Transpile
    transpile(vyper_ast)

    # Get transpiled Cairo in str format
    output = write(vyper_ast)

    # Write to output file
    write_cairo(output, output_file)


def signed_int_to_felt(i: int) -> int:
    """
    Convert negative python integer to its felt equivalent.
    """
    assert i < 0
    return CAIRO_PRIME + i
