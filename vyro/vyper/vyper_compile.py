import copy
from collections import OrderedDict
from pathlib import Path

from vyper import ast as vy_ast
from vyper.cli.vyper_compile import compile_files
from vyper.compiler.phases import generate_ast
from vyper.semantics import validate_semantics


def get_vyper_ast_dict(input_file: str, root_folder: str = ".") -> OrderedDict:

    return compile_files([input_file], ("ast",), root_folder)


def get_vyper_ast(file_name: str, root_folder: str = ".") -> vy_ast.Module:

    root_path = Path(root_folder).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Invalid root path - '{root_path.as_posix()}' does not exist")

    file_path = Path(file_name)
    with file_path.open() as fh:
        # trailing newline fixes python parsing bug when source ends in a comment
        # https://bugs.python.org/issue35107
        source_code = fh.read() + "\n"

    vyper_ast: vy_ast.Module = generate_ast(source_code, 0, file_name)
    vy_ast.validation.validate_literal_nodes(vyper_ast)
    vyper_ast_folded = copy.deepcopy(vyper_ast)
    vy_ast.folding.fold(vyper_ast_folded)
    validate_semantics(vyper_ast_folded, None)

    # Skip expansion of Vyper AST

    return vyper_ast_folded
