# built-in
import json
import sys

# app
from ._manager import read_setup


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    result = read_setup(path=argv[0])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0
