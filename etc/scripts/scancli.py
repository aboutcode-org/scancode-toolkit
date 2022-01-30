#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
from os.path import abspath
from os.path import dirname
from os.path import join
from os.path import normpath

import execnet

import scanserv

"""
This is a module designed to be called from Python 2 or 3 and is the client
side. See scanserv for the back server module that runs on Python 2 and runs
effectively scancode.
"""


def scan(locations, deserialize=False, scancode_root_dir=None):
    """
    Scan the list of paths at `location` and return the results as an iterable
    of JSON strings. If `deserialize` is True the iterable contains a python data
    instead.
    Each location is scanned independently.
    """
    if not scancode_root_dir:
        scancode_root_dir = abspath(normpath(__file__))
        scancode_root_dir = dirname(dirname(dirname(scancode_root_dir)))
    python2 = join(scancode_root_dir, "venv", "bin", "python")
    spec = "popen//python={python2}".format(**locals())
    gateway = execnet.makegateway(spec)  # NOQA
    channel = gateway.remote_exec(scanserv)

    for location in locations:
        # build a mapping of options to use for this scan
        scan_kwargs = dict(
            location=location,
            license=True,
            license_text=True,
            copyright=True,
            info=True,
            processes=0,
        )

        channel.send(scan_kwargs)  # execute func-call remotely
        results = channel.receive()
        if deserialize:
            results = json.loads(results)
        yield results


if __name__ == "__main__":
    import sys  # NOQA

    args = sys.argv[1:]
    for s in scan(args):
        print(s)
