from typing import Any, List, Tuple

from vyper.utils import bytes_to_int, string_to_bytes

from vyro.cairo.writer import write
from vyro.transpiler.transpile import transpile
from vyro.utils.output import write_cairo
from vyro.utils.utils import CAIRO_PRIME
from vyro.vyper.vyper_compile import get_vyper_ast


def transpile_to_cairo(path, output_file):
    vyper_ast = get_vyper_ast(path)

    # Transpile
    transpile(vyper_ast)

    # Get transpiled Cairo in str format
    output = write(vyper_ast)

    # Write to output file
    write_cairo(output, output_file)


def _replace_call_argument(args: List[Any], old: Any, new: Any):
    for idx, a in enumerate(args):
        if a == old:
            args[idx] = new


def replace_args(args: List[Any], replacements: List[Tuple[Any, Any]]):
    for r in replacements:
        old = r[0]
        new = r[1]
        _replace_call_argument(args, old, new)


def signed_int_to_felt(i: int) -> int:
    """
    Convert negative python integer to its felt equivalent.
    """
    assert i < 0
    return CAIRO_PRIME + i


def str_to_int(str_: str) -> int:
    b, _ = string_to_bytes(str_)
    ret = bytes_to_int(b)
    return ret
