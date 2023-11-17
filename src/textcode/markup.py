# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import Counter
import os
import re

from commoncode.text import as_unicode
from typecode import get_type

"""
Extract text from HTML, XML and related angular markup-like files.
"""

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_TEXT_ANALYSIS', False)


# Tracing flags
def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

bin_dir = os.path.join(os.path.dirname(__file__), 'bin')

extensions = ('.html', '.htm', '.php', '.phps', '.jsp', '.jspx' , '.xml', '.pom',)


def is_markup(location):
    """
    Return True is the file at `location` is some kind of markup, such as HTML,
    XML, PHP, etc.
    """
    T = get_type(location)

    # do not care for small files
    if T.size < 64:
        return False

    if not T.is_text:
        return False

    if location.endswith(extensions):
        return True

    with open(location, 'rb') as f:
        start = as_unicode(f.read(1024))

    return is_markup_text(start)


def is_markup_text(text):

    if text.startswith('<'):
        return True

    # count whitespaces
    no_spaces = ''.join(text.split())

    # count opening and closing tags_count
    counts = Counter(c for c in no_spaces if c in '<>')

    if not all(c in counts for c in '<>'):
        return False

    if not all(counts.values()):
        return False

    # ~ 5 percent of tag <> markers
    has_tags = sum(counts.values()) / len(no_spaces) > 0.05

    # check if we have some significant proportion of tag-like characters
    open_close = counts['>'] / counts['<']
    # ratio of open to close tags should approach 1: accept a 20% drift
    balanced = abs(1 - open_close) < .2
    return has_tags and balanced


def demarkup(location):
    """
    Return an iterator of unicode text lines for the file at `location` lightly
    stripping markup if the file is some kind of markup, such as HTML, XML, PHP,
    etc. The whitespaces are collapsed to one space.
    """
    from textcode.analysis import unicode_text_lines

    for line in unicode_text_lines(location):
        if TRACE:
            logger_debug(f'demarkup: {line} : demarked: {demarkup_text(line)}')
        yield demarkup_text(line)


get_tags_and_entities = re.compile(r'(</?[^\s></]+(?:>|\s)?|&[^\s&]+;|href|[\'"]?\/\>)', re.IGNORECASE).split


def demarkup_text(text):
    """
    Return text lightly stripped from markup. The whitespaces are collapsed to
    one space.
    """

    # keep the opening tag name of certain tags that contains these strings
    # note: <s> are from debian copyright files
    kept_tags = (
        'lic', 'copy', 'www', 'http', 'auth', 'contr', 'leg', 'inc', '@',
        '<s>', '</s>', '169', 'a9'
    )

    # find start and closing tags or the first white space whichever comes first
    # or entities. This regex is such that ' '.join(tags.split(a))==a

    tags_and_ents = get_tags_and_entities(text)
    if TRACE:
        logger_debug(f'demarkup_text: {text!r}')
        logger_debug(f'demarkup_text: tags_and_ents: {tags_and_ents}')

    cleaned = []
    cleaned_append = cleaned.append
    for token in tags_and_ents:
        tlow = token.lower()
        if tlow.startswith(('<', '&', 'href',)) and not any(k in tlow for k in kept_tags):
            continue
        else:
            cleaned_append(token)
    return u' '.join(cleaned)
