import json
import sys

from ._manager import ReadersManager


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    result = ReadersManager()(argv[0])
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0
