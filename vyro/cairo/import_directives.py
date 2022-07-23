from vyper import ast as vy_ast

from vyro.exceptions import TranspilerPanic

IMPORT_DIRECTIVES = {
    # Builtins
    "HashBuiltin": "starkware.cairo.common.cairo_builtins",
    # Syscalls
    "get_caller_address": "starkware.starknet.common.syscalls",
    "get_block_timestamp": "starkware.starknet.common.syscalls",
    # Constants
    "TRUE": "starkware.cairo.common.bool",
    "FALSE": "starkware.cairo.common.bool",
}


def add_builtin_to_module(node: vy_ast.Module, name: str):
    k = IMPORT_DIRECTIVES.get(name, None)
    if k:
        v = node._metadata["import_directives"].get(k, None)
        if v is None:
            s = set()
            s.add(name)
            node._metadata["import_directives"][k] = s
        else:
            node._metadata["import_directives"][k].add(name)

    else:
        raise TranspilerPanic(f"Unknown import: {name}")
