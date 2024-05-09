#
# Copyright (c) nexB Inc., Chris Liechti <cliechti@gmx.net> and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: BSD-3-Clause
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import re
import sys

"""
Utilities to find dunder variables in Python code.

The functions find_pattern(), find_dunder_version(), find_setup_py_dunder_version() are inspired
and heavily modified from Pyserial setup.py

https://github.com/pyserial/pyserial/blob/d867871e6aa333014a77498b4ac96fdd1d3bf1d8/setup.py
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def find_pattern(location, pattern):
    """
    Search the file at `location` for a patern regex on a single line and return
    this or None if not found. Reads the supplied location as text without
    importing it.

    """
    with open(location) as fp:
        content = fp.read()

    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()


def find_dunder_version(location):
    """
    Return a "dunder" __version__ string or None from searching the module file
    at `location`.
    """
    pattern = re.compile(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", re.MULTILINE)
    match = find_pattern(location, pattern)
    if TRACE: logger_debug('find_dunder_version:', 'location:', location, 'match:', match)
    return match


def find_setup_py_dunder_version(location):
    """
    Return a "dunder" __version__ expression string used as a setup(version)
    argument or None from searching the setup.py file at `location`.

    For instance:
        setup(
            version=six.__version__,
        ...
    would return six.__version__
    """
    pattern = re.compile(r"^\s*version\s*=\s*(.*__version__)", re.MULTILINE)
    match = find_pattern(location, pattern)
    if TRACE:
        logger_debug('find_setup_py_dunder_version:', 'location:', location, 'match:', match)
    return match
