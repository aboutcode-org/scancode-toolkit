# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import sys

from collections import deque

from commoncode.fileutils import file_name

"""
Detect and collect authors from a Linux-formatted CREDITS file.
This used by Linux, but also Raku, Phasar, u-boot, LLVM, Botan and other projects.
An enetry looks like this:
  N: Jack Lloyd
  E: lloyd@randombit.net
  W: http://www.randombit.net/
  P: 3F69 2E64 6D92 3BBE E7AE  9258 5C0F 96E8 4EC1 6D6B
  B: 1DwxWb2J4vuX4vjsbzaCXW696rZfeamahz

We only consider the entries: N: name, E: email and W: web URL
"""
# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_CREDITS', False)


# Tracing flags
def logger_debug(*args):
    pass


if TRACE:
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def is_credits_file(location):
    """
    Return True if the file is likely to be a credits file
    """
    credits_filenames = set([
        "credit",
        "credits",
        "credits.rst",
        "credits.txt",
        "credits.md",
        "author",
        "authors",
        "authors.rst",
        "authors.txt",
        "authors.md",
    ])

    fn = file_name(location).lower()
    return fn in credits_filenames


def detect_credits_authors(location):
    """
    Yield AuthorDetection objects detected in the CREDITS file at ``location``.
    """
    if not is_credits_file(location):
        return

    from textcode.analysis import numbered_text_lines

    numbered_lines = list(numbered_text_lines(location, demarkup=False))
    yield from detect_credits_authors_from_lines(numbered_lines)


def detect_credits_authors_from_lines(numbered_lines):
    """
    Yield AuthorDetection objects detected in the CREDITS file ``numbered_lines`` iterable of (line
    number, line text).
    """

    if TRACE:
        logger_debug('detect_credits_authors_from_lines: numbered_lines')
        for nl in numbered_lines:
            logger_debug('  numbered_line:', repr(nl))

    from cluecode.copyrights import AuthorDetection

    for lines in get_credit_lines_groups(numbered_lines):
        if TRACE:
            logger_debug('detect_credits_authors_from_lines: credit_lines group:', lines)

        start_line, _ = lines[0]
        end_line, _ = lines[-1]
        names = []
        emails = []
        webs = []
        for _, line in lines:
            ltype, _, line = line.partition(":")
            line = line.strip()
            if ltype == "N":
                names.append(line)
            elif ltype == "E":
                emails.append(line)
            elif ltype == "W":
                webs.append(line)

        items = list(" ".join(item) for item in (names, emails, webs) if item)
        if TRACE:
            logger_debug('detect_credits_authors_from_lines: items:', items)

        author = " ".join(items)
        if author:
            yield AuthorDetection(author=author, start_line=start_line, end_line=end_line)


def get_credit_lines_groups(numbered_lines):
    """
    Yield groups of contiguous credit lines as separated by one of more empty lines.
    Only keep line of interest.
    """
    lines_group = []
    lines_group_append = lines_group.append
    lines_group_clear = lines_group.clear

    has_credits = False
    for ln, line in numbered_lines:
        line = line.strip()

        if not line and lines_group:
            if TRACE:
                logger_debug('get_credit_lines_groups: lines_group:', lines_group)

            yield list(lines_group)
            lines_group_clear()

        if line.startswith(("N:", "E:", "W:")):
            has_credits = True
            lines_group_append((ln, line))

        # bail out if there are no structured credits in the first 50 lines
        if ln > 50 and not has_credits:
            return

    if lines_group:
        yield list(lines_group)
