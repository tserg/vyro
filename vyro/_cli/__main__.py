import importlib
import sys
import traceback
from pathlib import Path

from vyro._config import __version__
from vyro.utils.docopt import docopt, levenshtein_norm

__doc__ = """Usage: vyro <command> [<args>...] [options <args>]

Commands:
  transpile             Transpile a Vyper contract to Cairo.
  test                  Run test cases in the tests/ folder.

Options:
  --help -h             Display this message.
  --version             Show version and exit.
"""


def main():

    print(f"Vyro v{__version__} - Transpiler for Vyper to Cairo\n")

    if "--version" in sys.argv:
        sys.exit()

    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        # this call triggers a SystemExit
        docopt(__doc__, ["vyro", "-h"])

    if "-i" in sys.argv:
        # a small kindness to ipython users
        sys.argv[sys.argv.index("-i")] = "-I"

    cmd = sys.argv[1]
    cmd_list = [i.stem for i in Path(__file__).parent.glob("[!_]*.py")]
    if cmd not in cmd_list:
        distances = sorted(
            [(i, levenshtein_norm(cmd, i)) for i in cmd_list], key=lambda k: k[1]
        )
        if distances[0][1] <= 0.2:
            sys.exit(f"Invalid command. Did you mean 'vyro {distances[0][0]}'?")
        sys.exit("Invalid command. Try 'vyro --help' for available commands.")

    sys.tracebacklimit = 1000

    try:
        importlib.import_module(f"vyro._cli.{cmd}").main()
    except Exception as e:
        tb_item = sys.exc_info()[2]
        traceback.print_tb(tb_item)
        print(e)
