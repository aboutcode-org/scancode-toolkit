# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import re
import sys
from collections import deque
from time import time

import attr
from pygmars import lex
from pygmars import parse
from pygmars import Token
from pygmars import tree

from commoncode.text import toascii
from commoncode.text import unixlinesep

from cluecode import copyrights_hint

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_COPYRIGHT', False)

# set to 1 to enable pygmars deep tracing
TRACE_DEEP = 0
if os.environ.get('SCANCODE_DEBUG_COPYRIGHT_DEEP'):
    TRACE_DEEP = 1
    TRACE = False

TRACE_TOK = False or os.environ.get('SCANCODE_DEBUG_COPYRIGHT_TOKEN', False)

VALIDATE = False or os.environ.get('SCANCODE_DEBUG_COPYRIGHT_VALIDATE', False)


# Tracing flags
def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP or TRACE_TOK:
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

"""
Detect and collect copyright statements.

The process consists in:
 - prepare and cleanup text

 - identify regions of text that may contain copyright (using hints).
   These are called "candidates".

 - tag the text to recognize (e.g. lex) parts-of-speech (POS) tags to identify
   various copyright statements parts such as dates, companies, names
   ("named entities"), etc. This is done using pygmars which contains a lexer
   derived from NLTK POS tagger.

 - feed the tagged text to a parsing grammar describing actual copyright
   statements (also using pygmars) and obtain a parse tree.

 - Walk the parse tree and yield Detection objects (e.g., copyright statements,
   holder or authors) with start and end line from the parse tree with some
   extra post-detection cleanups.
"""


def detect_copyrights(
    location,
    include_copyrights=True,
    include_holders=True,
    include_authors=True,
    include_copyright_years=True,
    include_copyright_allrights=False,
    demarkup=True,
    deadline=sys.maxsize,
):
    """
    Yield Detection objects detected in the file at ``location``.

    The flags ``include_copyrights``, ``include_holders`` and
    ``include_authors`` drive which actual detections are done and returned.

    For copyrights only:
    - If ``include_copyright_years`` is True, include years and year ranges.
    - If ``include_copyright_allrights`` is True, include trailing
      "all rights reserved"-style mentions

    Strip markup from text if ``demarkup`` is True.
    Run for up to ``deadline`` seconds and return results found so far.
    """
    from textcode.analysis import numbered_text_lines

    numbered_lines = numbered_text_lines(location, demarkup=demarkup)
    numbered_lines = list(numbered_lines)

    if TRACE:
        logger_debug('detect_copyrights: numbered_lines')
        for nl in numbered_lines:
            logger_debug('  numbered_line:', repr(nl))

    include_copyright_years = include_copyrights and include_copyright_years
    include_copyright_allrights = include_copyrights and include_copyright_allrights

    yield from detect_copyrights_from_lines(
        numbered_lines=numbered_lines,
        include_copyrights=include_copyrights,
        include_holders=include_holders,
        include_authors=include_authors,
        include_copyright_years=include_copyright_years,
        include_copyright_allrights=include_copyright_allrights,
        deadline=deadline,
    )


DETECTOR = None


def detect_copyrights_from_lines(
    numbered_lines,
    include_copyrights=True,
    include_holders=True,
    include_authors=True,
    include_copyright_years=True,
    include_copyright_allrights=False,
    deadline=sys.maxsize,
):
    """
    Yield Detection objects detected in a ``numbered_lines`` sequence of
    tuples of (line number, text).

    The flags ``include_copyrights``, ``include_holders`` and
    ``include_authors`` drive which actual detections are done and returned.

    For copyrights only:
    - If ``include_copyright_years`` is True, include years and year ranges.
    - If ``include_copyright_allrights`` is True, include trailing
      "all rights reserved"-style mentions

    Run for up to ``deadline`` seconds and return results found so far.
    """
    if not numbered_lines:
        return

    include_copyright_years = include_copyrights and include_copyright_years
    include_copyright_allrights = include_copyrights and include_copyright_allrights

    global DETECTOR

    if not DETECTOR:
        DETECTOR = detector = CopyrightDetector()
    else:
        detector = DETECTOR

    candidate_lines_groups = candidate_lines(numbered_lines)

    if TRACE:
        candidate_lines_groups = list(candidate_lines_groups)
        logger_debug(
            f'detect_copyrights_from_lines: ALL groups of candidate '
            f'lines collected: {len(candidate_lines_groups)}',
        )

    for candidates in candidate_lines_groups:
        if TRACE:
            from pprint import pformat
            can = pformat(candidates, width=160)
            logger_debug(
                f' detect_copyrights_from_lines: processing candidates group:\n'
                f'  {can}'
            )

        detections = detector.detect(
            numbered_lines=candidates,
            include_copyrights=include_copyrights,
            include_holders=include_holders,
            include_authors=include_authors,
            include_copyright_years=include_copyright_years,
            include_copyright_allrights=include_copyright_allrights
        )

        if TRACE:
            detections = list(detections)
            logger_debug(f' detect_copyrights_from_lines: {detections}')

        for detection in detections:
            yield detection

        # TODO: return a warning if we missed the deadline
        if time() > deadline:
            break

################################################################################
# DETECTION PROPER
################################################################################


class CopyrightDetector(object):
    """
    Detect copyrights and authors.
    """

    def __init__(self):
        self.lexer = lex.Lexer(patterns)
        self.parser = parse.Parser(grammar, trace=TRACE_DEEP, validate=VALIDATE)

    def detect(self,
        numbered_lines,
        include_copyrights=True,
        include_holders=True,
        include_authors=True,
        include_copyright_years=True,
        include_copyright_allrights=False,
    ):
        """
        Yield Detection objects detected in a ``numbered_lines`` sequence of
        tuples of (line number, text).

        The flags ``include_copyrights``, ``include_holders`` and
        ``include_authors`` drive which actual detections are done and returned.

        For copyrights only:
        - If ``include_copyright_years`` is True, include years and year ranges.
        - If ``include_copyright_allrights`` is True, include trailing
          "all rights reserved"-style mentions
        """

        include_copyright_years = include_copyrights and include_copyright_years
        include_copyright_allrights = include_copyrights and include_copyright_allrights

        numbered_lines = list(numbered_lines)
        if not numbered_lines:
            return

        if TRACE:
            logger_debug(f'CopyrightDetector: numbered_lines: {numbered_lines}')

        tokens = list(get_tokens(numbered_lines))

        if TRACE:
            logger_debug(f'CopyrightDetector: initial tokens: {tokens}')

        if not tokens:
            return

        # first, POS tag each token using token regexes
        lexed_text = list(self.lexer.lex_tokens(tokens))

        if TRACE:
            logger_debug(f'CopyrightDetector: lexed tokens: {lexed_text}')

        # then build a parse parse_tree based on tagged tokens
        parse_tree = self.parser.parse(lexed_text)

        if TRACE:
            logger_debug(f'CopyrightDetector: parse_tree: {parse_tree}')

        non_copyright_labels = frozenset()
        if not include_copyright_years:
            non_copyright_labels = frozenset([
                'YR-RANGE', 'YR', 'YR-AND', 'YR-PLUS', 'BARE-YR',
            ])

        non_holder_labels = frozenset([
            'COPY',
            'YR-RANGE', 'YR-AND', 'YR', 'YR-PLUS', 'BARE-YR',
            'EMAIL', 'URL',
            'HOLDER', 'AUTHOR',
        ])

        non_holder_labels_mini = frozenset([
            'COPY',
            'YR-RANGE', 'YR-AND', 'YR', 'YR-PLUS', 'BARE-YR',
            'HOLDER', 'AUTHOR',
        ])

        non_authors_labels = frozenset([
            'COPY',
            'YR-RANGE', 'YR-AND', 'YR', 'YR-PLUS', 'BARE-YR',
            'HOLDER', 'AUTHOR',
        ])

        # then walk the parse parse_tree, collecting copyrights, years and authors
        for tree_node in parse_tree:
            if not isinstance(tree_node, tree.Tree):
                continue

                if TRACE:
                    logger_debug(f'CopyrightDetector: parse_tree node: {tree_node}')

            tree_node_label = tree_node.label

            if (include_copyrights or include_holders) and 'COPYRIGHT' in tree_node_label:
                copyrght = build_detection_from_node(
                    node=tree_node,
                    cls=CopyrightDetection,
                    ignores=non_copyright_labels,
                    include_copyright_allrights=include_copyright_allrights,
                    refiner=refine_copyright,
                    junk=COPYRIGHTS_JUNK,
                )

                if TRACE:
                    logger_debug(f'CopyrightDetector: detection: {copyrght}')

                if copyrght:
                    if include_copyrights:
                        yield copyrght

                    if include_holders:
                        # By default we strip email and urls from holders ....
                        holder = build_detection_from_node(
                            node=tree_node,
                            cls=HolderDetection,
                            ignores=non_holder_labels,
                            refiner=refine_holder,
                        )

                        if not holder:
                            # ... but if we have no holder, we try again and
                            # this time we keep email and URLs for holders using
                            # "non_holder_labels_mini" as an "ignores" label set
                            holder = build_detection_from_node(
                                node=tree_node,
                                cls=HolderDetection,
                                ignores=non_holder_labels_mini,
                                refiner=refine_holder,
                            )

                        if holder:
                            if TRACE:
                                logger_debug(f'CopyrightDetector: holders: {holder}')

                            yield holder

            elif include_authors and tree_node_label == 'AUTHOR':
                author = build_detection_from_node(
                    node=tree_node,
                    cls=AuthorDetection,
                    ignores=non_authors_labels,
                    refiner=refine_author,
                    junk=AUTHORS_JUNK,
                )

                if author:
                    if TRACE:
                        logger_debug(f'CopyrightDetector: detected authors: {author}')

                    yield author


def get_tokens(numbered_lines, splitter=re.compile('[\\t =;]+').split):
    """
    Return an iterable of pygmars.Token built from a ``numbered_lines`` iterable
    of tuples of (line number, text).

    We perform a simple tokenization on spaces, tabs and some punctuation =;
    """
    for start_line, line in numbered_lines:
        if TRACE_TOK:
            logger_debug('  get_tokens: bare line: ' + repr(line))

        line = prepare_text_line(line)

        if TRACE_TOK:
            logger_debug('  get_tokens: preped line: ' + repr(line))

        pos = 0
        for tok in splitter(line):
            # FIXME: strip trailing single quotes and ignore empties
            tok = tok.strip("' ")
            # FIXME: strip trailing colons: why?
            tok = tok.rstrip(':').strip()
            # FIXME: strip leading @: : why?
            tok = tok.lstrip('@').strip()
            # FIXME: why?
            if tok and tok != ':':
                yield Token(value=tok, start_line=start_line, pos=pos)
                pos += 1


class Detection:

    def to_dict(self):
        """
        Return a dict of primitive Python types.
        """
        return attr.asdict(self)

    @classmethod
    def split(cls, detections, to_dict=False):
        """
        Return a list of CopyrightDetection, a list of HolderDetection and a
        list of AuthorDetection given a ``detections`` list of Detection.
        If ``to_dict`` is True, return lists of mappings instead of objects.
        """
        copyrights = []
        holders = []
        authors = []

        for detection in detections:
            det = detection.to_dict() if to_dict else detection
            if isinstance(detection, CopyrightDetection):
                copyrights.append(det)
            elif isinstance(detection, HolderDetection):
                holders.append(det)
            elif isinstance(detection, AuthorDetection):
                authors.append(det)
        return copyrights, holders, authors

    @classmethod
    def split_values(cls, detections):
        """
        Return a list of copyright strings, a list of holder strings and a
        list of author strings given a ``detections`` list of Detection.
        """
        copyrights, holders, authors = cls.split(detections)
        copyrights = [det.copyright for det in copyrights]
        holders = [det.holder for det in holders]
        authors = [det.author for det in authors]
        return copyrights, holders, authors


@attr.s(slots=True)
class CopyrightDetection(Detection):
    copyright = attr.ib()
    start_line = attr.ib()
    end_line = attr.ib()


@attr.s(slots=True)
class HolderDetection(Detection):
    holder = attr.ib()
    start_line = attr.ib()
    end_line = attr.ib()


@attr.s(slots=True)
class AuthorDetection(Detection):
    author = attr.ib()
    start_line = attr.ib()
    end_line = attr.ib()


def build_detection_from_node(
    node,
    cls,
    ignores=frozenset(),
    include_copyright_allrights=False,
    refiner=None,
    junk=frozenset(),
):
    """
    Return a ``cls`` Detection object from a pygmars.tree.Tree ``node`` with a
    space-normalized string value or None.

    Filter ``node`` Tokens with a type found in the ``ignores`` set of ignorable
    token types.

    For copyright detection, include trailing "All rights reserved" if
    ``include_copyright_allrights`` is True.

    Apply the ``refiner`` callable function to the detection string.

    Return None if the value exists in the ``junk`` strings set.
    """
    include_copyright_allrights = (
        cls == CopyrightDetection
        and include_copyright_allrights
    )

    if ignores:
        leaves = [
            token for token in node.leaves()
            if token.label not in ignores
        ]
    else:
        leaves = node.leaves()

    # if TRACE_DEEP:  logger_debug('    starting leaves:', leaves)

    if include_copyright_allrights:
        filtered = leaves
    else:
        filtered = []

        for token in leaves:
            # FIXME: this should operate on the tree and not on the leaves
            # ALLRIGHTRESERVED: <NNP|NN|CAPS> <RIGHT> <NNP|NN|CAPS>? <RESERVED>

            # This pops ALL RIGHT RESERVED by finding it backwards from RESERVED
            if token.label == 'RESERVED':
                if (
                    len(filtered) >= 2
                    and filtered[-1].label == 'RIGHT'
                    and filtered[-2].label in ('NN', 'CAPS', 'NNP')
                ):
                    filtered = filtered[:-2]
                elif (
                    len(filtered) >= 3
                    and filtered[-1].label in ('NN', 'CAPS', 'NNP')
                    and filtered[-2].label == 'RIGHT'
                    and filtered[-3].label in ('NN', 'CAPS', 'NNP')
                ):
                    filtered = filtered[:-3]
            else:
                filtered.append(token)

    node_string = ' '.join(t.value for t in filtered)
    node_string = ' '.join(node_string.split())

    if refiner:
        node_string = refiner(node_string)

    if node_string and node_string.lower() not in junk:
        start_line = filtered[0].start_line
        end_line = filtered[-1].start_line

        return cls(node_string, start_line=start_line, end_line=end_line)

################################################################################
# LEXING AND PARSING
################################################################################


_YEAR = (r'('
    '19[6-9][0-9]'  # 1960 to 1999
    '|'
    '20[0-2][0-9]'  # 2000 to 2019
')')

_YEAR_SHORT = (r'('
    '[6-9][0-9]'  # 60 to 99
    '|'
    '[0-][0-9]'  # 00 to 29
')')

_YEAR_YEAR = (r'('
              # fixme   v ....the underscore below is suspicious
    '(19[6-9][0-9][\\.,\\-]_)+[6-9][0-9]'  # 1960-99
    '|'
    '(19[6-9][0-9][\\.,\\-])+[0-9]'  # 1998-9
    '|'
    '(20[0-2][0-9][\\.,\\-])+[0-2][0-9]'  # 2001-16 or 2012-04
    '|'
    '(20[0-2][0-9][\\.,\\-])+[0-9]'  # 2001-4 not 2012
    '|'
    '(20[0-2][0-9][\\.,\\-])+20[0-2][0-9]'  # 2001-2012
')')

_PUNCT = (r'('
    '['
        '\\W'  # not a word (word includes underscore)
        '\\D'  # not a digit
        '\\_'  # underscore
        'i'  # oddity
        '\\?'
    ']'
    '|'
    '\\&nbsp'  # html entity sometimes are double escaped
')*')  # repeated 0 or more times

_YEAR_PUNCT = _YEAR + _PUNCT
_YEAR_YEAR_PUNCT = _YEAR_YEAR + _PUNCT
_YEAR_SHORT_PUNCT = _YEAR_SHORT + _PUNCT

_YEAR_OR_YEAR_YEAR_WITH_PUNCT = (r'(' +
    _YEAR_PUNCT +
    '|' +
    _YEAR_YEAR_PUNCT +
')')

_YEAR_THEN_YEAR_SHORT = (r'(' +
    _YEAR_OR_YEAR_YEAR_WITH_PUNCT +
    '(' +
    _YEAR_SHORT_PUNCT +
    ')*' +
')')

# TODO: this needs to be simplified:

patterns = [
    ############################################################################
    # COPYRIGHT
    ############################################################################

    # some exceptions

    # NOT a copyright Copyright.txt : treat as NN
    (r'^Copyright\.txt$', 'NN'),

    # when lowercase with trailing period. this is not a Copyright statement
    (r'^copyright\.\)?$', 'NN'),

    # NOT a copyright symbol (ie. "copyrighted."): treat as NN
    (r'^Copyrighted[\.,]$', 'NN'),
    (r'^Copyrights[\.,]$', 'NN'),
    (r'^copyrighted[\.,]$', 'NN'),
    (r'^copyrights[\.,]$', 'NN'),
    (r'^COPYRIGHTS[\.,]$', 'NN'),
    (r'^COPYRIGHTED[\.,]$', 'NN'),

    # copyright word or symbol
    (r'^[\(\.@_\-\#\):]*[Cc]opyrights?:?$', 'COPY'),
    (r'^[\(\.@_]*COPYRIGHT[sS]?:?$', 'COPY'),
    (r'^[\(\.@]*[Cc]opyrighted?:?$', 'COPY'),
    (r'^[\(\.@]*COPYRIGHTED?:?$', 'COPY'),
    (r'^[\(\.@]*CopyRights?:?$', 'COPY'),

    # with a trailing comma
    (r'^Copyright,$', 'COPY'),

    (r'^\(C\)\,?$', 'COPY'),
    (r'^\(c\)\,?$', 'COPY'),

    (r'^COPR\.?$', 'COPY'),
    (r'^copr\.?$', 'COPY'),
    (r'^Copr\.?$', 'COPY'),

    # copyright in markup, until we strip markup: apache'>Copyright
    (r'[A-Za-z0-9]+[\'">]+[Cc]opyright', 'COPY'),

    # A copyright line in some manifest, meta or structured files such Windows PE
    (r'^AssemblyCopyright.?$', 'COPY'),
    (r'^AppCopyright?$', 'COPY'),

    # SPDX-FileCopyrightText as defined by the FSFE Reuse project
    (r'^[Ss][Pp][Dd][Xx]-[Ff]ile[Cc]opyright[Tt]ext', 'COPY'),

    # SPDX-FileContributor as defined in SPDX and seen used in KDE
    (r'^[Ss][Pp][Dd][Xx]-[Ff]ile[Cc]ontributor', 'SPDX-CONTRIB'),

    ############################################################################
    # ALL Rights Reserved.
    ############################################################################
    # All|Some|No Rights Reserved. should be a terminator/delimiter.
    (r'^All$', 'NN'),
    (r'^all$', 'NN'),
    (r'^ALL$', 'NN'),
    (r'^NO$', 'NN'),
    (r'^No$', 'NN'),
    (r'^no$', 'NN'),
    (r'^Some$', 'NN'),
    (r'^[Rr]ights?$', 'RIGHT'),
    (r'^RIGHTS?$', 'RIGHT'),
    (r'^[Rr]eserved[\.,]*$', 'RESERVED'),
    (r'^RESERVED[\.,]*$', 'RESERVED'),
    (r'^[Rr]eversed[\.,]*$', 'RESERVED'),
    (r'^REVERSED[\.,]*$', 'RESERVED'),

    # in German
    (r'^[Aa]lle$', 'NN'),
    (r'^[Rr]echte$', 'RIGHT'),
    (r'^[Vv]orbehalten[\.,]*$', 'RESERVED'),

    # in French
    (r'^[Tt]ous$', 'NN'),
    (r'^[Dr]roits?$', 'RIGHT'),
    (r'^[Rr]éservés[\.,]*$', 'RESERVED'),
    (r'^[Rr]eserves[\.,]*$', 'RESERVED'),

    ############################################################################
    # JUNK are things to ignore
    ############################################################################

    # path with trailing year-like are NOT a year as in
    # Landroid/icu/impl/IDNA2003 : treat as JUNK
    (r'^[^\\/]+[\\/][^\\/]+[\\/].*$', 'JUNK'),

    # Combo of many (3+) letters and punctuations groups without spaces is likely junk
    # "AEO>>,o>>'!xeoI?o?O1/4thuA/"
    # (r'((\w+\W+){3,})+', 'JUNK'),

    # CamELCaseeXXX is typcally JUNK such as code variable names
    # AzaAzaaaAz BBSDSB002923,
    (r'^([A-Z][a-z]+){3,20}[A-Z]+[0-9]*,?$', 'JUNK'),

    # multiple parens (at least two (x) groups) is a sign of junk
    # such as in (1)(ii)(OCT
    (r'^.*\(.*\).*\(.*\).*$', 'JUNK'),

    # parens such as (1) or (a) is a sign of junk but of course NOT (c)
    (r'^\(([abdefghi\d]|ii|iii)\)$', 'JUNK'),

    # found in crypto certificates and LDAP
    (r'^O=$', 'JUNK'),
    (r'^OU=?$', 'JUNK'),
    (r'^XML$', 'JUNK'),
    (r'^Parser$', 'JUNK'),
    (r'^Dual$', 'JUNK'),
    (r'^Crypto$', 'JUNK'),
    (r'^PART$', 'JUNK'),
    (r'^[Oo]riginally?$', 'JUNK'),
    (r'^[Rr]epresentations?\.?$', 'JUNK'),
    (r'^works,$', 'JUNK'),

    (r'^Refer$', 'JUNK'),
    (r'^Apt$', 'JUNK'),
    (r'^Agreement$', 'JUNK'),
    (r'^Usage$', 'JUNK'),
    (r'^Please$', 'JUNK'),
    (r'^\(?Based$', 'JUNK'),
    (r'^Upstream$', 'JUNK'),
    (r'^Files?$', 'JUNK'),
    (r'^Filename:?$', 'JUNK'),
    (r'^Description:?$', 'JUNK'),
    (r'^[Pp]rocedures?$', 'JUNK'),
    (r'^You$', 'JUNK'),
    (r'^Everyone$', 'JUNK'),
    (r'^Unless$', 'JUNK'),
    (r'^rant$', 'JUNK'),
    (r'^Subject$', 'JUNK'),
    (r'^Acknowledgements?$', 'JUNK'),
    (r'^Special$', 'JUNK'),
    (r'^Derivative$', 'JUNK'),
    (r'^[Ll]icensable$', 'JUNK'),
    (r'^[Ss]ince$', 'JUNK'),
    (r'^[Ll]icen[cs]e[\.d]?$', 'JUNK'),
    (r'^[Ll]icen[cs]ors?$', 'JUNK'),
    (r'^under$', 'JUNK'),
    (r'^TCK$', 'JUNK'),
    (r'^Use$', 'JUNK'),
    (r'^[Rr]estrictions?$', 'JUNK'),
    (r'^[Ii]ntrodu`?ction$', 'JUNK'),
    (r'^[Ii]ncludes?$', 'JUNK'),
    (r'^[Vv]oluntary$', 'JUNK'),
    (r'^[Cc]ontributions?$', 'JUNK'),
    (r'^[Mm]odifications?$', 'JUNK'),
    (r'^Company:$', 'JUNK'),
    (r'^For$', 'JUNK'),
    (r'^File$', 'JUNK'),
    (r'^Last$', 'JUNK'),
    (r'^[Rr]eleased?$', 'JUNK'),
    (r'^[Cc]opyrighting$', 'JUNK'),
    (r'^[Aa]uthori.*$', 'JUNK'),
    (r'^such$', 'JUNK'),
    (r'^[Aa]ssignments?[.,]?$', 'JUNK'),
    (r'^[Bb]uild$', 'JUNK'),
    (r'^[Ss]tring$', 'JUNK'),
    (r'^Implementation-Vendor$', 'JUNK'),
    (r'^dnl$', 'JUNK'),
    (r'^rem$', 'JUNK'),
    (r'^REM$', 'JUNK'),
    (r'^Supports$', 'JUNK'),
    (r'^Separator$', 'JUNK'),
    (r'^\.byte$', 'JUNK'),
    (r'^Idata$', 'JUNK'),
    (r'^[Cc]ontributed?$', 'JUNK'),
    (r'^[Ff]unctions?$', 'JUNK'),
    (r'^[Nn]otices?$', 'JUNK'),
    (r'^[Mm]ust$', 'JUNK'),
    (r'^ISUPPER?$', 'JUNK'),
    (r'^ISLOWER$', 'JUNK'),
    (r'^AppPublisher$', 'JUNK'),

    (r'^DISCLAIMS?$', 'JUNK'),
    (r'^SPECIFICALLY$', 'JUNK'),

    (r'^IDENTIFICATION$', 'JUNK'),
    (r'^WARRANTIE?S?$', 'JUNK'),
    (r'^WARRANTS?$', 'JUNK'),
    (r'^WARRANTYS?$', 'JUNK'),

    (r'^hispagestyle$', 'JUNK'),
    (r'^Generic$', 'JUNK'),
    (r'^Change$', 'JUNK'),
    (r'^Add$', 'JUNK'),
    (r'^Generic$', 'JUNK'),
    (r'^Average$', 'JUNK'),
    (r'^Taken$', 'JUNK'),
    (r'^LAWS\.?$', 'JUNK'),
    (r'^design$', 'JUNK'),
    (r'^Driver$', 'JUNK'),
    (r'^[Cc]ontribution\.?', 'JUNK'),

    (r'DeclareUnicodeCharacter$', 'JUNK'),
    (r'^Language-Team$', 'JUNK'),
    (r'^Last-Translator$', 'JUNK'),
    (r'^OMAP730$', 'JUNK'),
    (r'^Law\.$', 'JUNK'),
    (r'^dylid$', 'JUNK'),
    (r'^BeOS$', 'JUNK'),
    (r'^Generates?$', 'JUNK'),
    (r'^Thanks?$', 'JUNK'),
    (r'^therein$', 'JUNK'),

    # various programming constructs
    (r'^var$', 'JUNK'),
    (r'^[Tt]his$', 'JUNK'),
    (r'^return$', 'JUNK'),
    (r'^function$', 'JUNK'),
    (r'^thats?$', 'JUNK'),
    (r'^xmlns$', 'JUNK'),
    (r'^file$', 'JUNK'),
    (r'^[Aa]sync$', 'JUNK'),
    (r'^Keyspan$', 'JUNK'),

    # neither and nor conjunctions and some common licensing words are NOT part
    # of a copyright statement
    (r'^neither$', 'JUNK'),
    (r'^nor$', 'JUNK'),

    (r'^providing$', 'JUNK'),
    (r'^Execute$', 'JUNK'),
    (r'^NOTICE[.,]*$', 'JUNK'),
    (r'^[Nn]otice[.,]*$', 'JUNK'),
    (r'^passes$', 'JUNK'),
    (r'^Should$', 'JUNK'),
    (r'^[Ll]icensing\@?$', 'JUNK'),
    (r'^Disclaimer$', 'JUNK'),
    (r'^LAWS\,?$', 'JUNK'),
    (r'^[Ll]aws?,?$', 'JUNK'),
    (r'^Some$', 'JUNK'),
    (r'^Derived$', 'JUNK'),
    (r'^Limitations?$', 'JUNK'),
    (r'^Nothing$', 'JUNK'),
    (r'^Policy$', 'JUNK'),
    (r'^available$', 'JUNK'),
    (r'^Recipient\.?$', 'JUNK'),
    (r'^LICEN[CS]EES?\.?$', 'JUNK'),
    (r'^[Ll]icen[cs]ees?,?$', 'JUNK'),
    (r'^Application$', 'JUNK'),
    (r'^Receiving$', 'JUNK'),
    (r'^Party$', 'JUNK'),
    (r'^interfaces$', 'JUNK'),
    (r'^owner$', 'JUNK'),
    (r'^Sui$', 'JUNK'),
    (r'^Generis$', 'JUNK'),
    (r'^Conditioned$', 'JUNK'),
    (r'^Disclaimer$', 'JUNK'),
    (r'^Warranty$', 'JUNK'),
    (r'^Represents$', 'JUNK'),
    (r'^Sufficient$', 'JUNK'),
    (r'^Each$', 'JUNK'),
    (r'^Partially$', 'JUNK'),
    (r'^Limitation$', 'JUNK'),
    (r'^Liability$', 'JUNK'),
    (r'^Named$', 'JUNK'),
    (r'^Use.$', 'JUNK'),
    (r'^EXCEPT$', 'JUNK'),
    (r'^OWNER\.?$', 'JUNK'),
    (r'^Comments\.?$', 'JUNK'),
    (r'^you$', 'JUNK'),
    (r'^means$', 'JUNK'),
    (r'^information$', 'JUNK'),
    (r'^[Aa]lternatively.?$', 'JUNK'),
    (r'^[Aa]lternately.?$', 'JUNK'),
    (r'^INFRINGEMENT.?$', 'JUNK'),
    (r'^Install$', 'JUNK'),
    (r'^Updates$', 'JUNK'),
    (r'^Record-keeping$', 'JUNK'),
    (r'^Privacy$', 'JUNK'),
    (r'^within$', 'JUNK'),

    # various trailing words that are junk
    (r'^Copyleft$', 'JUNK'),
    (r'^LegalCopyright$', 'JUNK'),
    (r'^Distributed$', 'JUNK'),
    (r'^Report$', 'JUNK'),
    (r'^Available$', 'JUNK'),
    (r'^true$', 'JUNK'),
    (r'^false$', 'JUNK'),
    (r'^node$', 'JUNK'),
    (r'^jshint$', 'JUNK'),
    (r'^node\':true$', 'JUNK'),
    (r'^node:true$', 'JUNK'),
    (r'^this$', 'JUNK'),
    (r'^Act,?$', 'JUNK'),
    (r'^[Ff]unctionality$', 'JUNK'),
    (r'^bgcolor$', 'JUNK'),
    (r'^F+$', 'JUNK'),
    (r'^Rewrote$', 'JUNK'),
    (r'^Much$', 'JUNK'),
    (r'^remains?,?$', 'JUNK'),
    (r'^earlier$', 'JUNK'),
    (r'^is$', 'JUNK'),
    (r'^[lL]aws?$', 'JUNK'),
    (r'^Insert$', 'JUNK'),
    (r'^url$', 'JUNK'),
    (r'^[Ss]ee$', 'JUNK'),
    (r'^[Pp]ackage\.?$', 'JUNK'),
    (r'^Covered$', 'JUNK'),
    (r'^date$', 'JUNK'),
    (r'^practices$', 'JUNK'),
    (r'^[Aa]ny$', 'JUNK'),
    (r'^ANY$', 'JUNK'),
    (r'^fprintf.*$', 'JUNK'),
    (r'^CURDIR$', 'JUNK'),
    (r'^Environment/Libraries$', 'JUNK'),
    (r'^Environment/Base$', 'JUNK'),
    (r'^Violations\.?$', 'JUNK'),
    (r'^Owner$', 'JUNK'),
    (r'^behalf$', 'JUNK'),
    (r'^know-how$', 'JUNK'),
    (r'^interfaces?,?$', 'JUNK'),
    (r'^than$', 'JUNK'),
    (r'^whom$', 'JUNK'),
    (r'^are$', 'JUNK'),
    (r'^However,?$', 'JUNK'),
    (r'^[Cc]ollectively$', 'JUNK'),
    (r'^following$', 'JUNK'),
    (r'^file\.$', 'JUNK'),
    # version variables listed after Copyright variable in FFmpeg
    (r'^ExifVersion$', 'JUNK'),
    (r'^FlashpixVersion$', 'JUNK'),
    (r'^.+ArmsAndLegs$', 'JUNK'),

    # junk when HOLDER(S): typically used in disclaimers instead
    (r'^HOLDER\(S\)$', 'JUNK'),

    # some HTML tags
    (r'^width$', 'JUNK'),

    # this trigger otherwise "copyright ownership. The ASF" in Apache license headers
    (r'^[Oo]wnership\.?$', 'JUNK'),

    # exceptions to composed proper namess, mostly debian copyright/control tag-related
    # FIXME: may be lowercase instead?
    (r'^Title:?$', 'JUNK'),
    (r'^Debianized-By:?$', 'JUNK'),
    (r'^Upstream-Maintainer:?$', 'JUNK'),
    (r'^Content', 'JUNK'),
    (r'^Upstream-Author:?$', 'JUNK'),
    (r'^Packaged-By:?$', 'JUNK'),

    # Windows XP
    (r'^Windows$', 'JUNK'),
    (r'^XP$', 'JUNK'),
    (r'^SP1$', 'JUNK'),
    (r'^SP2$', 'JUNK'),
    (r'^SP3$', 'JUNK'),
    (r'^SP4$', 'JUNK'),
    (r'^assembly$', 'JUNK'),

    # various junk bits
    (r'^example\.com$', 'JUNK'),
    (r'^null$', 'JUNK'),
    (r'^:Licen[cs]e$', 'JUNK'),
    (r'^Agent\.?$', 'JUNK'),
    (r'^behalf$', 'JUNK'),
    (r'^[aA]nyone$', 'JUNK'),

    # when uppercase this is likely part of some SQL statement
    (r'^FROM$', 'JUNK'),
    (r'^CREATE$', 'JUNK'),
    (r'^CURDIR$', 'JUNK'),
    # found in sqlite
    (r'^\+0$', 'JUNK'),
    (r'^ToUpper$', 'JUNK'),

    # Java
    (r'^.*Servlet,?$', 'JUNK'),
    (r'^class$', 'JUNK'),

    # C/C++
    (r'^template$', 'JUNK'),
    (r'^struct$', 'JUNK'),
    (r'^typedef$', 'JUNK'),
    (r'^type$', 'JUNK'),
    (r'^next$', 'JUNK'),
    (r'^typename$', 'JUNK'),
    (r'^namespace$', 'JUNK'),
    (r'^type_of$', 'JUNK'),
    (r'^begin$', 'JUNK'),
    (r'^end$', 'JUNK'),

    # Some mixed case junk
    (r'^LastModified$', 'JUNK'),

    # Some font names
    (r'^Lucida$', 'JUNK'),

    # various trailing words that are junk
    (r'^CVS$', 'JUNK'),
    (r'^EN-IE$', 'JUNK'),
    (r'^Info$', 'JUNK'),
    (r'^GA$', 'JUNK'),
    (r'^unzip$', 'JUNK'),
    (r'^EULA', 'JUNK'),
    (r'^Terms?[.,]?$', 'JUNK'),
    (r'^Non-Assertion$', 'JUNK'),

    # this is not Copr.
    (r'^Coproduct,?[,\.]?$$', 'JUNK'),

    # FIXME: may be these should be NNs?
    (r'^CONTRIBUTORS?[,\.]?$', 'JUNK'),
    (r'^OTHERS?[,\.]?$', 'JUNK'),
    (r'^Contributors?\:[,\.]?$', 'JUNK'),
    (r'^Version$', 'JUNK'),

    # JUNK from binary
    (r'^x1b|1H$', 'JUNK'),

    # JUNK as camel case with a single hump such as in "processingInfo"
    (r'^[a-z]{3,10}[A-Z][a-z]{3,10}$', 'JUNK'),

    (r'^\$?Guid$', 'JUNK'),
    (r'^Small$', 'NN'),

    ############################################################################
    # Nouns and proper Nouns
    ############################################################################

    # Various rare bits treated as NAME directly
    (r'^FSFE?[\.,]?$', 'NAME'),
    (r'^This_file_is_part_of_KDE$', 'NAME'),

    # K.K. (a company suffix), needs special handling
    (r'^K.K.,?$', 'NAME'),

    # MIT is problematic
    # With a comma, always CAPS (MIT alone is too error prone to be always tagged as CAPS
    (r'^MIT,$', 'CAPS'),
    (r'^MIT\.?$', 'MIT'),
    # MIT is common enough, but not with a trailing period.
    (r'^MIT$', 'NN'),

    # ISC is always a company
    (r'^MIT$', 'COMP'),

    # NOT A CAPS
    # [YEAR] W3C® (MIT, ERCIM, Keio, Beihang)."
    (r'^YEAR', 'NN'),

    # Various NN, exceptions to NNP or CAPS: note that some are open ended and
    # do not end with a $

    (r'^Activation\.?$', 'NN'),
    (r'^Act[\.,]?$', 'NN'),
    (r'^Added$', 'NN'),
    (r'^Are$', 'NN'),
    (r'^Additional$', 'NN'),
    (r'^AGPL.?$', 'NN'),
    (r'^Agreements?\.?$', 'NN'),
    (r'^AIRTM$', 'NN'),
    (r'^Android$', 'NN'),
    (r'^Any$', 'NN'),
    (r'^Appropriate', 'NN'),
    (r'^APPROPRIATE', 'NN'),
    (r'^Asset$', 'NN'),
    (r'^Assignment', 'NN'),
    (r'^Atomic$', 'NN'),
    (r'^Attribution$', 'NN'),
    (r'^[Aa]uthored$', 'NN'),
    (r'^Baslerstr\.?$', 'NN'),
    (r'^BSD$', 'NN'),
    (r'^BUT$', 'NN'),
    (r'^But$', 'NN'),
    (r'^Cases$', 'NN'),
    (r'^Change\.?[lL]og$', 'NN'),
    (r'^CHANGElogger$', 'NN'),
    (r'^CHANGELOG$', 'NN'),
    (r'^CHANGES$', 'NN'),
    (r'^Code$', 'NN'),
    (r'^Commercial', 'NN'),
    (r'^Commons$', 'NN'),
    # TODO: Compilation could be JUNK?
    (r'^Compilation', 'NN'),
    (r'^Contact', 'NN'),
    (r'^Contracts?$', 'NN'),
    (r'^Convention$', 'NN'),
    (r'^Copying', 'NN'),
    (r'^COPYING', 'NN'),
    (r'^Customer', 'NN'),
    (r'^Custom$', 'NN'),
    (r'^Data$', 'NN'),
    (r'^Date$', 'NN'),
    (r'^DATED', 'NN'),
    (r'^Delay', 'NN'),
    (r'^Derivative', 'NN'),
    (r'^DISCLAIMED', 'NN'),
    (r'^Docs?$', 'NN'),
    (r'^DOCUMENTATION', 'NN'),
    (r'^DOM$', 'NN'),
    (r'^Do$', 'NN'),
    (r'^DoubleClick$', 'NN'),
    (r'^Each$', 'NN'),
    (r'^Education$', 'NN'),
    (r'^E-?[Mm]ail\:?$', 'NN'),
    (r'^END$', 'NN'),
    (r'^Entity$', 'NN'),
    (r'^Example', 'NN'),
    (r'^Except', 'NN'),
    (r'^Experimental$', 'NN'),
    (r'^F2Wku$', 'NN'),
    (r'^False$', 'NN'),
    (r'^FALSE$', 'NN'),
    (r'^FAQ', 'NN'),
    (r'^Foreign', 'NN'),
    (r'^From$', 'NN'),
    (r'^Further', 'NN'),
    (r'^Gaim$', 'NN'),
    (r'^Generated', 'NN'),
    (r'^Glib$', 'NN'),
    (r'^GPLd', 'NN'),
    (r'^GPL\'d', 'NN'),
    (r'^Gnome$', 'NN'),
    (r'^GnuPG$', 'NN'),
    (r'^Government.', 'NNP'),
    (r'^Government', 'NN'),
    (r'^Grants?\.?,?$', 'NN'),
    (r'^Header', 'NN'),
    (r'^HylaFAX$', 'NN'),
    (r'^IA64$', 'NN'),
    (r'^IDEA$', 'NN'),
    (r'^Id$', 'NN'),
    (r'^IDENTIFICATION?\.?$', 'NN'),
    (r'^IEEE$', 'NN'),
    (r'^If$', 'NN'),
    (r'^[Ii]ntltool$', 'NN'),
    (r'^Immediately$', 'NN'),
    (r'^Implementation', 'NN'),
    (r'^Improvement', 'NN'),
    (r'^INCLUDING', 'NN'),
    (r'^Indemnification', 'NN'),
    (r'^Indemnified', 'NN'),
    (r'^Information', 'NN'),
    (r'^In$', 'NN'),
    (r'^Intellij$', 'NN'),
    (r'^ISC-LICENSE$', 'NN'),
    (r'^IS$', 'NN'),
    (r'^It$', 'NN'),
    (r'^Java$', 'NN'),
    (r'^JavaScript$', 'NN'),
    (r'^JMagnetic$', 'NN'),
    (r'^Joint$', 'NN'),
    (r'^Jsunittest$', 'NN'),
    (r'^List$', 'NN'),
    (r'^Set$', 'NN'),
    (r'^Last$', 'NN'),
    (r'^LAW', 'NN'),
    (r'^Legal$', 'NN'),
    (r'^LegalTrademarks$', 'NN'),
    (r'^Library$', 'NN'),
    (r'^Libraries$', 'NN'),
    (r'^Licen[cs]e', 'NN'),
    (r'^License-Alias\:?$', 'NN'),
    (r'^Linux$', 'NN'),
    (r'^Locker$', 'NN'),
    (r'^Log$', 'NN'),
    (r'^Logos?$', 'NN'),
    (r'^Luxi$', 'NN'),
    (r'^Mac$', 'NN'),
    (r'^Manager$', 'NN'),
    (r'^Material$', 'NN'),
    (r'^Mode$', 'NN'),
    (r'^Modified$', 'NN'),
    (r'^Mouse$', 'NN'),
    (r'^Module$', 'NN'),
    (r'^Natural$', 'NN'),
    (r'^New$', 'NN'),
    (r'^NEWS$', 'NN'),
    (r'^Neither$', 'NN'),
    (r'^Norwegian$', 'NN'),
    (r'^Notes?$', 'NN'),
    (r'^NOTICE', 'NN'),
    (r'^NOT$', 'NN'),
    (r'^NULL$', 'NN'),
    (r'^Objects$', 'NN'),
    (r'^Open$', 'NN'),
    (r'^Operating$', 'NN'),
    (r'^OriginalFilename$', 'NN'),
    (r'^Original$', 'NN'),
    (r'^OR$', 'NN'),
    (r'^OWNER', 'NN'),
    (r'^Package$', 'NN'),
    (r'^PACKAGE$', 'NN'),
    (r'^Packaging$', 'NN'),
    (r'^Patent', 'NN'),
    (r'^Pentium$', 'NN'),
    (r'^[Pp]ermission', 'NN'),
    (r'^PERMISSIONS?', 'NN'),
    (r'^PGP$', 'NN'),
    (r'^Phrase', 'NN'),
    (r'^Plugin', 'NN'),
    (r'^Policy', 'NN'),
    (r'^POSIX$', 'NN'),
    (r'^Possible', 'NN'),
    (r'^Powered$', 'NN'),
    (r'^Predefined$', 'NN'),
    (r'^Products?\.?$', 'NN'),
    (r'^PROFESSIONAL?\.?$', 'NN'),
    (r'^Programming$', 'NN'),
    (r'^PROOF', 'NN'),
    (r'^PROVIDED$', 'NN'),
    (r'^Public\.?$', 'NN'),
    (r'^Qualified$', 'NN'),
    (r'^RCSfile$', 'NN'),
    (r'^README$', 'NN'),
    (r'^Read$', 'NN'),
    (r'^RECURSIVE$', 'NN'),
    (r'^Redistribution', 'NN'),
    (r'^References', 'NN'),
    (r'^Related$', 'NN'),
    (r'^Release', 'NN'),
    (r'^Revision', 'NN'),
    (r'^RIGHT', 'NN'),
    (r'^[Rr]espective', 'NN'),
    (r'^SAX$', 'NN'),
    (r'^Section', 'NN'),
    (r'^Send$', 'NN'),
    (r'^Separa', 'NN'),
    (r'^Service$', 'NN'),
    (r'^Several$', 'NN'),
    (r'^SIGN$', 'NN'),
    (r'^Site\.?$', 'NN'),
    (r'^Statement', 'NN'),
    (r'^software$', 'NN'),
    (r'^SOFTWARE$', 'NN'),
    (r'^So$', 'NN'),
    (r'^Sort$', 'NN'),
    (r'^Source$', 'NN'),
    (r'^Standard$', 'NN'),
    (r'^Std$', 'NN'),
    (r'^Supplicant', 'NN'),
    (r'^Support', 'NN'),
    (r'^TagSoup$', 'NN'),
    (r'^Target$', 'NN'),
    (r'^Technical$', 'NN'),
    (r'^Termination$', 'NN'),
    (r'^The$', 'NN'),
    (r'^THE', 'NN'),
    (r'^These$', 'NN'),
    (r'^[tT]here$', 'NN'),
    (r'^This$', 'NN'),
    (r'^THIS$', 'NN'),
    (r'^Those$', 'NN'),
    (r'^Timer', 'NN'),
    (r'^TODO$', 'NN'),
    (r'^Tool.?$', 'NN'),
    (r'^Trademarks?$', 'NN'),
    (r'^True$', 'NN'),
    (r'^TRUE$', 'NN'),
    (r'^[Tt]ext$', 'NN'),
    (r'^Unicode$', 'NN'),
    (r'^Updated', 'NN'),
    (r'^URL$', 'NN'),
    (r'^Users?$', 'NN'),
    (r'^VALUE$', 'NN'),
    (r'^Various', 'NN'),
    (r'^Vendor', 'NN'),
    (r'^VIEW$', 'NN'),
    (r'^Visit', 'NN'),
    (r'^Website', 'NN'),
    (r'^Wheel$', 'NN'),
    (r'^Win32$', 'NN'),
    (r'^Work', 'NN'),
    (r'^WPA$', 'NN'),
    (r'^Xalan$', 'NN'),
    (r'^YOUR', 'NN'),
    (r'^Your', 'NN'),
    (r'^DateTime', 'NN'),
    (r'^Create$', 'NN'),
    (r'^Engine\.$', 'NN'),
    (r'^While$', 'NN'),
    (r'^Review', 'NN'),
    (r'^Help', 'NN'),
    (r'^Web', 'NN'),

    # alone this is not enough for an NNP
    (r'^Free$', 'NN'),

    # Hours/Date/Day/Month text references
    (r'^am$', 'NN'),
    (r'^pm$', 'NN'),
    (r'^AM$', 'NN'),
    (r'^PM$', 'NN'),

    (r'^January$', 'NN'),
    (r'^February$', 'NN'),
    (r'^March$', 'NN'),
    (r'^April$', 'NN'),
    (r'^May$', 'NN'),
    (r'^June$', 'NN'),
    (r'^July$', 'NN'),
    (r'^August$', 'NN'),
    (r'^September$', 'NN'),
    (r'^October$', 'NN'),
    (r'^November$', 'NN'),
    (r'^December$', 'NN'),

    (r'^Name[\.,]?$', 'NN'),
    (r'^Co-Author[\.,]?$', 'NN'),
    (r'^Author\'s$', 'NN'),
    (r'^Co-Author\'s$', 'NN'),
    #  the Universal Copyright Convention (1971 Paris text).
    (r'^Convention[\.,]?$', 'NN'),
    (r'^Paris[\.,]?$', 'NN'),

    # we do not include Jan and Jun that are common enough first names
    (r'^(Feb|Mar|Apr|May|Jul|Aug|Sep|Oct|Nov|Dec)$', 'NN'),
    (r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$', 'NN'),
    (r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$', 'NN'),

    ############################################################################
    # Proper Nouns
    ############################################################################

    # Title case word with a trailing parens is an NNP
    (r'^[A-Z][a-z]{3,}\)$', 'NNP'),

    # names with a slash that are NNP
    # Research/Unidata, LCS/Telegraphics.
    (r'^('
       r'[A-Z]'
       r'([a-z]|[A-Z])+'
       r'/'
       r'[A-Z][a-z]+[\.,]?'
     r')$', 'NNP'),

    # communications
    (r'communications', 'NNP'),

    # Places: TODO: these are NOT NNPs but we treat them as such for now
    (r'^\(?'
     r'(?:Cambridge|Stockholm|Davis|Sweden[\)\.]?'
     r'|Massachusetts'
     r'|Oregon'
     r'|California'
     r'|Norway'
     r'|UK'
     r'|Berlin'
     r'|CONCORD'
     r'|Manchester'
     r'|MASSACHUSETTS'
     r'|Finland'
     r'|Espoo'
     r'|Munich'
     r'|Germany'
     r'|Italy'
     r'|Spain'
     r'|Europe'
     r'|Lafayette'
     r'|Indiana'
     r')[\),\.]?$', 'NNP'),

    # Misc corner case combos ?(mixed, NN or CAPS) that are NNP
    (r'^Software,\',$', 'NNP'),
    (r'\(Royal$', 'NNP'),
    (r'PARADIGM$', 'NNP'),
    (r'vFeed$', 'NNP'),
    (r'nexB$', 'NNP'),
    (r'UserTesting$', 'NNP'),
    (r'D\.T\.Shield\.?$', 'NNP'),
    (r'Antill\',$', 'NNP'),

    # Corner cases of lowercased NNPs
    (r'^suzuki$', 'NNP'),
    (r'toshiya\.?$', 'NNP'),
    (r'leethomason$', 'NNP'),
    (r'finney$', 'NNP'),
    (r'sean$', 'NNP'),
    (r'chris$', 'NNP'),
    (r'ulrich$', 'NNP'),
    (r'wadim$', 'NNP'),
    (r'dziedzic$', 'NNP'),
    (r'okunishinishi$', 'NNP'),
    (r'yiminghe$', 'NNP'),
    (r'daniel$', 'NNP'),
    (r'wirtz$', 'NNP'),
    (r'vonautomatisch$', 'NNP'),
    (r'werkstaetten\.?$', 'NNP'),
    (r'werken$', 'NNP'),
    (r'various\.?$', 'NNP'),

    # treat Attributable as proper noun as it is seen in Author tags such as in:
    # @author not attributable
    (r'^[Aa]ttributable$', 'NNP'),

    # rarer caps
    # EPFL-LRC/ICA
    (r'^[A-Z]{3,6}-[A-Z]{3,6}/[A-Z]{3,6}', 'NNP'),

    ############################################################################
    # Named entities: companies, groups, universities, etc
    ############################################################################

    # AT&T (the company), needs special handling
    (r'^AT\&T[\.,]?$', 'COMP'),

    # company suffix name with  suffix Tech.,ltd
    (r'^[A-Z][a-z]+[\.,]+(LTD|LTd|LtD|Ltd|ltd|lTD|lTd|ltD).?,?$', 'COMP'),

    # company suffix
    (r'^[Ii]nc[.]?[,\.]?\)?$', 'COMP'),
    (r'^Incorporated[,\.]?\)?$', 'COMP'),

    # ,Inc. suffix without spaces is directly a company name
    (r'^.+,Inc\.$', 'COMPANY'),

    (r'^[Cc]ompany[,\.]?\)?$', 'COMP'),
    (r'^Limited[,\.]??$', 'COMP'),
    (r'^LIMITED[,\.]??$', 'COMP'),

    # Caps company suffixes
    (r'^INC[\.,\)]*$', 'COMP'),
    (r'^INCORPORATED[\.,\)]*$', 'COMP'),
    (r'^CORP[\.,\)]*$', 'COMP'),
    (r'^CORPORATION[\.,\)]*$', 'COMP'),
    (r'^FOUNDATION[\.,\)]*$', 'COMP'),
    (r'^GROUP[\.,\)]*$', 'COMP'),
    (r'^COMPANY[\.,\)]*$', 'COMP'),
    (r'^\(tm\)[\.,]?$', 'COMP'),
    (r'^[Ff]orum[\.,\)]*', 'COMP'),

    # company suffix
    (r'^[Cc]orp[\.,\)]*$', 'COMP'),
    (r'^[Cc]orporation[\.,\)]*$', 'COMP'),
    (r'^[Cc][oO][\.,\)]*$', 'COMP'),
    (r'^[Cc]orporations?[\.,\)]*$', 'COMP'),
    (r'^[Cc]onsortium[\.,\)]*$', 'COMP'),

    (r'^[Ff]oundation[\.,\)]*$', 'COMP'),
    (r'^[Aa]lliance[\.,\)]*$', 'COMP'),
    (r'^Working$', 'COMP'),
    (r'^[Gg]roup[\.,\)]*$', 'COMP'),
    (r'^[Tt]echnolog(y|ies)[\.,\)]*$', 'COMP'),
    (r'^[Cc]ommunit(y|ies)[\.,\)]*$', 'COMP'),
    (r'^[Mm]icrosystems[\.,\)]*$', 'COMP'),
    (r'^[Pp]rojects?[\.,\)]*,?$', 'COMP'),
    (r'^[Tt]eams?[\.,\)]*$', 'COMP'),
    (r'^[Tt]ech[\.,\)]*$', 'COMP'),
    (r"^Limited'?[\.,\)]*$", 'COMP'),

    # company suffix : LLC, LTD, LLP followed by one extra char
    (r'^[Ll][Tt][Dd]\.?,?$', 'COMP'),
    (r'^[Ll]\.?[Ll]\.?[CcPp]\.?,?$', 'COMP'),
    (r'^L\.P\.?$', 'COMP'),
    (r'^[Ss]ubsidiary$', 'COMP'),
    (r'^[Ss]ubsidiaries\.?$', 'COMP'),
    (r'^[Ss]ubsidiary\(\-ies\)\.?$', 'COMP'),

    # company suffix : SA, SAS, AG, AB, AS, CO, labs followed by a dot
    (r'^(S\.?A\.?S?|Sas|sas|A\/S|AG,?|AB|Labs?|[Cc][Oo]|Research|Center|INRIA|Societe)\.?$', 'COMP'),
    # French SARL
    (r'^(SARL|S\.A\.R\.L\.)[\.,\)]*$', 'COMP'),
    # company suffix : AS: this is frequent beyond Norway.
    (r'^AS.$', 'COMP'),
    (r'^AS', 'CAPS'),

    # (german) company suffix
    (r'^[Gg][Mm][Bb][Hh].?$', 'COMP'),
    # ( e.V. german) company suffix
    (r'^[eV]\.[vV]\.?$', 'COMP'),
    # (italian) company suffix
    (r'^[sS]\.[pP]\.[aA]\.?$', 'COMP'),
    # sweedish company suffix : ASA followed by a dot
    (r'^ASA.?$', 'COMP'),
    # czech company suffix: JetBrains s.r.o.
    (r'^s\.r\.o\.?$', 'COMP'),
    # (Laboratory) company suffix
    (r'^(Labs?|Laboratory|Laboratories|Laboratoire)\.?,?$', 'COMP'),
    # (dutch and belgian) company suffix
    (r'^[Bb]\.?[Vv]\.?|BVBA$', 'COMP'),
    # university
    (r'^\(?[Uu]niv(?:[.]|ersit(?:y|e|at?|ad?))[\.,\)]*$', 'UNI'),
    (r'^UNIVERSITY$', 'UNI'),
    (r'^College$', 'UNI'),
    # Academia/ie
    (r'^[Ac]cademi[ae]s?$', 'UNI'),
    # Academia/ie
    (r'^[Ac]cademy[\.,\)]*$', 'UNI'),

    # institutes
    (r'INSTITUTE', 'COMP'),
    (r'^\(?[Ii]nstitut(s|o|os|e|es|et|a|at|as|u|i)?\)?$', 'COMP'),

    # Facility
    (r'Facility', 'COMP'),

    (r'Tecnologia', 'COMP'),

    # (danish) company suffix
    (r'^ApS|A\/S|IVS\.?,?$', 'COMP'),

    # (finnsih) company suffix
    (r'^Abp\.?,?$', 'COMP'),

    # "holders" is considered Special
    (r'^([Hh]olders?|HOLDERS?).?$', 'HOLDER'),

    # affiliates or "and its affiliate(s)."
    (r'^[Aa]ffiliate(s|\(s\))?\.?$', 'NNP'),

    # OU as in Org unit, found in some certficates
    (r'^OU$', 'OU'),

    ############################################################################
    # AUTHORS
    ############################################################################

    # "authors" or "contributors" is interesting, and so a tag of its own
    (r'^[Aa]uthor$', 'AUTH'),
    (r'^[Aa]uthors?\.$', 'AUTHDOT'),
    (r'^Authors$', 'AUTHS'),
    (r'^authors|author\'$', 'AUTHS'),
    (r'^[Aa]uthor\(s\)\.?$', 'AUTHS'),
    (r'^@author$', 'AUTH'),

    (r'^[Cc]ontribut(ors|ing)\.?$', 'CONTRIBUTORS'),
    (r'^contributors,$', 'CONTRIBUTORS'),

    (r'^Contributor[,.]?$', 'NN'),
    (r'^Licensor[,.]?$', 'NN'),

    # same for developed, etc...
    (r'^[Cc]oded$', 'AUTH2'),
    (r'^[Rr]ecoded$', 'AUTH2'),
    (r'^[Mm]odified$', 'AUTH2'),
    (r'^[Cc]reated$', 'AUTH2'),
    (r'^[Ww]ritten$', 'AUTH2'),
    (r'^[Mm]aintained$', 'AUTH2'),
    (r'^[Dd]eveloped$', 'AUTH2'),

    # commiters is interesting, and so a tag of its own
    (r'[Cc]ommitters\.??', 'COMMIT'),

    # same for maintainers, developers, admins.
    (r'^[Aa]dmins?$', 'MAINT'),
    (r'^[Dd]evelopers?\.?$', 'MAINT'),
    (r'^[Mm]aintainers?\.?$', 'MAINT'),
    (r'^co-maintainers?$', 'MAINT'),

    ############################################################################
    # Conjunctions and related
    ############################################################################

    (r'^OF$', 'OF'),
    (r'^of$', 'OF'),
    (r'^Of$', 'OF'),

    # DE/de/di: OF:
    # FIXME this conflicts with VAN??
    (r'^De$', 'OF'),
    (r'^DE$', 'OF'),
    (r'^Di$', 'OF'),
    (r'^di$', 'OF'),

    # in
    (r'^in$', 'IN'),
    (r'^en$', 'IN'),

    # by
    (r'^by$', 'BY'),
    (r'^BY$', 'BY'),
    (r'^By$', 'BY'),

    # conjunction: and
    (r'^and$', 'CC'),
    (r'^And$', 'CC'),
    (r'^AND$', 'CC'),
    (r'^and/or$', 'CC'),
    (r'^&$', 'CC'),
    (r'^at$', 'CC'),
    (r'^et$', 'CC'),
    (r'^Et$', 'CC'),
    (r'^ET$', 'CC'),
    (r'^Und$', 'CC'),
    (r'^und$', 'CC'),

    # solo comma as a conjunction
    (r'^,$', 'CC'),

    # ie. in things like "Copyright (c) 2012 John Li and others"
    # or et.al.
    (r'^[Oo]ther?s[\.,]?$', 'OTH'),
    (r'^et\. ?al[\.,]?$', 'OTH'),

    # in year ranges: dash, or 'to': "1990-1995", "1990/1995" or "1990 to 1995"
    (r'^-$', 'DASH'),
    (r'^/$', 'DASH'),

    (r'^to$', 'TO'),

    # Portions copyright .... are worth keeping
    (r'[Pp]ortions?|[Pp]arts?', 'PORTIONS'),

    # in dutch/german names, like Marco van Basten, or Klemens von Metternich
    # and Spanish/French Da Siva and De Gaulle
        (r'^(([Vv][ao]n)|[Dd][aeu])$', 'VAN'),

    (r'^van$', 'VAN'),
    (r'^Van$', 'VAN'),
    (r'^von$', 'VAN'),
    (r'^Von$', 'VAN'),
    (r'^Da$', 'VAN'),
    (r'^da$', 'VAN'),
    (r'^De$', 'VAN'),
    (r'^de$', 'VAN'),
    (r'^Du$', 'VAN'),
    (r'^du$', 'VAN'),

    ############################################################################
    # Years and Year ranges
    ############################################################################

    # rare cases of trailing + signon years
    (r'^20[0-1][0-9]\+$', 'YR-PLUS'),

    # year or year ranges
    # plain year with various leading and trailing punct
    # dual or multi years 1994/1995. or 1994-1995
    # 1987,88,89,90,91,92,93,94,95,96,98,99,2000,2001,2002,2003,2004,2006
    # multi years
    # dual years with second part abbreviated
    # 1994/95. or 2002-04 or 1991-9
    (r'^' + _PUNCT + _YEAR_OR_YEAR_YEAR_WITH_PUNCT + '+' +
        '(' +
            _YEAR_OR_YEAR_YEAR_WITH_PUNCT +
        '|' +
            _YEAR_THEN_YEAR_SHORT +
        ')*' + '$', 'YR'),

    (r'^' + _PUNCT + _YEAR_OR_YEAR_YEAR_WITH_PUNCT + '+' +
        '(' +
            _YEAR_OR_YEAR_YEAR_WITH_PUNCT +
        '|' +
            _YEAR_THEN_YEAR_SHORT +
        '|' +
            _YEAR_SHORT_PUNCT +
        ')*' + '$', 'YR'),

    (r'^(' + _YEAR_YEAR + ')+$', 'YR'),

    # 88, 93, 94, 95, 96: this is a pattern mostly used in FSF copyrights
    (r'^[8-9][0-9],$', 'YR'),

    # 80 to 99: this is a pattern mostly used in FSF copyrights
    (r'^[8-9][0-9]$', 'BARE-YR'),

    # weird year
    (r'today.year', 'YR'),
    (r'^\$?LastChangedDate\$?$', 'YR'),

    # Copyright templates in W3C documents
    (r'^\$?date-of-software$', 'YR'),
    (r'^\$?date-of-document$', 'YR'),

    # cardinal numbers
    (r'^-?[0-9]+(.[0-9]+)?.?$', 'CD'),

    ############################################################################
    # All caps and proper nouns
    ############################################################################

    # composed proper nouns, ie. Jean-Claude or ST-Microelectronics
    # FIXME: what about a variant with spaces around the dash?
    (r'^[A-Z][a-zA-Z]*\s?[\-]\s?[A-Z]?[a-zA-Z]+.?$', 'NNP'),

    # Countries abbreviations
    (r'^U\.S\.A\.?$', 'NNP'),

    # Dotted ALL CAPS initials
    (r'^([A-Z]\.){1,3}$', 'NNP'),

    # misc corner cases such LaTeX3 Project and other
    (r'^LaTeX3$', 'NNP'),
    (r'^Meridian\'93$', 'NNP'),
    (r'^Xiph.Org$', 'NNP'),
    (r'^iClick,?$', 'NNP'),

    # proper nouns with digits
    (r'^([A-Z][a-z0-9]+){1,2}\.?$', 'NNP'),

    # saxon genitive, ie. Philippe's
    (r"^[A-Z][a-z]+[']s$", 'NNP'),

    # Uppercase dotted name, ie. P. or DMTF.
    (r'^([A-Z]+\.)+$', 'PN'),

    # proper noun with some separator and trailing comma
    (r'^[A-Z]+[.][A-Z][a-z]+[,]?$', 'NNP'),

    # proper noun with apostrophe ': D'Orleans, D'Arcy, T'so, Ts'o
    (r"^[A-Z][a-z]?['][A-Z]?[a-z]+[,.]?$", 'NNP'),

    # proper noun with apostrophe ': d'Itri
    (r"^[a-z]['][A-Z]?[a-z]+[,\.]?$", 'NNP'),

    # all CAPS word, at least 1 char long such as MIT, including an optional trailing comma or dot
    (r'^[A-Z0-9]+[,]?$', 'CAPS'),

    # all caps word 3 chars and more, enclosed in parens
    (r'^\([A-Z0-9]{2,}\)$', 'CAPS'),

    # all CAPS word, all letters including an optional trailing single quote
    (r"^[A-Z]{2,}\'?$", 'CAPS'),

    # proper noun: first CAP, including optional trailing comma
    # note: this also captures a bare comma as an NNP ... this is a bug
    (r'^([A-Z][a-zA-Z0-9]+){,2}\.?,?$', 'NNP'),

    ############################################################################
    # URLS and emails
    ############################################################################

     # email start-at-end: <sebastian.classen at freenet.ag>: <EMAIL_START> <AT> <EMAIL_END>
    (r'^<([a-zA-Z]+[a-zA-Z\.]){2,5}$', 'EMAIL_START'),
    (r'^[a-zA-Z\.]{2,5}>$', 'EMAIL_END'),

    # a .sh shell scripts is NOT an email.
    (r'^.*\.sh\.?$', 'JUNK'),
    # email eventually in parens or brackets with some trailing punct.
    (r'^[\<\(]?[a-zA-Z0-9]+[a-zA-Z0-9\+_\-\.\%]*(@|at)[a-zA-Z0-9][a-zA-Z0-9\+_\-\.\%]+\.[a-zA-Z]{2,5}?[\>\)\.\,]*$', 'EMAIL'),

    # URLS such as <(http://fedorahosted.org/lohit)> or ()
    (r'[<\(]https?:.*[>\)]', 'URL'),
    # URLS such as ibm.com without a scheme
    (r'\s?[a-z0-9A-Z\-\.\_]+\.([Cc][Oo][Mm]|[Nn][Ee][Tt]|[Oo][Rr][Gg]|us|mil|io|edu|co\.[a-z][a-z]|eu|ch|fr|de|be|se|nl|au|biz)\s?\.?$', 'URL2'),
    # TODO: add more extensions: there are so main TLD these days!
    # URL wrapped in () or <>
    (r'[\(<]+\s?[a-z0-9A-Z\-\.\_]+\.(com|net|org|us|mil|io|edu|co\.[a-z][a-z]|eu|ch|fr|jp|de|be|se|nl|au|biz)\s?[\.\)>]+$', 'URL'),
    (r'<?a?.(href)?.\(?[a-z0-9A-Z\-\.\_]+\.(com|net|org|us|mil|io|edu|co\.[a-z][a-z]|eu|ch|fr|jp|de|be|se|nl|au|biz)[\.\)>]?$', 'URL'),
    # derived from regex in cluecode.finder
    (r'<?a?.(href)?.('
     r'(?:http|ftp|sftp)s?://[^\s<>\[\]"]+'
     r'|(?:www|ftp)\.[^\s<>\[\]"]+'
     r')\.?>?', 'URL'),

    (r'^\(?<?https?://[a-zA-Z0-9_\-]+(\.([a-zA-Z0-9_\-])+)+.?\)?>?$', 'URL'),

    # URLS with trailing/ such as http://fedorahosted.org/lohit/
    # URLS with leading( such as (http://qbnz.com/highlighter/
    (r'\(?https?:.*/', 'URL'),

    ############################################################################
    # Misc
    ############################################################################

    # .\" is not a noun
    (r'^\.\\\?"?$', 'JUNK'),

    # Mixed cap nouns (rare) LeGrande
    (r'^[A-Z][a-z]+[A-Z][a-z]+[\.\,]?$', 'MIXEDCAP'),

    # Code variable names including snake case
    (r'^.*(_.*)+$', 'JUNK'),

    # !$?
    (r'^\!\$\?$', 'JUNK'),

    # things composed only of non-word letters (e.g. junk punctuations)
    # but keeping _ ? and () as parts of words
    (r'^[^\w\?()]{2,10}$', 'JUNK'),

    ############################################################################
    # catch all other as Nouns
    ############################################################################

    # nouns (default)
    (r'.+', 'NN'),
]

# Comments in the Grammar are lines that start with #
# End of line commenst are rules descriptions.
# One rule per line.
grammar = """

#######################################
# YEARS
#######################################

    YR-RANGE: {<YR>+ <CC>+ <YR>}        #20
    YR-RANGE: {<YR> <DASH|TO>* <YR|BARE-YR>+}        #30
    YR-RANGE: {<CD|BARE-YR>? <YR> <BARE-YR>?}        #40
    YR-RANGE: {<YR>+ <BARE-YR>? }        #50
    YR-AND: {<CC>? <YR>+ <CC>+ <YR>}        #60
    YR-RANGE: {<YR-AND>+}        #70|
    YR-RANGE: {<YR-RANGE>+ <DASH|TO> <YR-RANGE>+}        #71
    YR-RANGE: {<YR-RANGE>+ <DASH>?}        #72

    CD: {<BARE-YR>} #bareyear

#######################################
# All/No/Some Rights Reserved
#######################################

    # All/No/Some Rights Reserved OR  All Rights Are Reserved
    ALLRIGHTRESERVED: {<NNP|NN|CAPS> <RIGHT> <NNP|NN|CAPS>? <RESERVED>}  #allrightsreserved


#######################################
# COMPOSITE emails
#######################################

    EMAIL: {<EMAIL_START> <CC> <NN>* <EMAIL_END>} # composite_email

#######################################
# NAMES and COMPANIES
#######################################

    # two CC such as ", and" are treated as a single CC
    CC: {<CC><CC>} #73

    NAME: {<NAME><NNP>} #75

    NAME: {<NN|NNP> <CC> <URL|URL2>} #80

    # the Tor Project, Inc.
    COMP: {<COMP> <COMP>+} #81

    # Laboratory for Computer Science Research Computing Facility
    COMPANY: {<COMP> <NN> <NNP> <NNP> <COMP> <NNP> <COMP>} #83
    COMPANY: {<COMP> <NN> <NNP> <NNP> <COMP>} #82

    # E. I. du Pont de Nemours and Company
    COMPANY: {<NNP> <NNP> <VAN> <NNP> <OF> <NNP> <CC> <COMP>}             #1010

    #  Robert A. van Engelen OR NetGroup, Politecnico di Torino (Italy)
    NAME: {<NNP>+ <VAN|OF> <NNP>+} #88

    NAME: {<NNP> <VAN|OF> <NN*> <NNP>}        #90

    NAME: {<NNP> <PN> <VAN> <NNP>}        #100

    # by the netfilter coreteam <coreteam@netfilter.org>
    NAME: {<BY> <NN>+ <EMAIL>}        #110

    # Kaleb S. KEITHLEY
    NAME: {<NNP> <PN> <CAPS>}        #120

    # Trolltech AS, Norway.
    NAME: {<NNP> <CAPS> <NNP>}        #121

    # BY GEORGE J. CARRETTE
    NAME: {<BY> <CAPS> <PN> <CAPS>} #85

    DASHCAPS: {<DASH> <CAPS>}
   # INRIA - CIRAD - INRA
    COMPANY: {<COMP> <DASHCAPS>+}        #1280

    # Project Admins leethomason
    COMPANY: {<COMP> <MAINT> <NNP>+}        #1281

    # the Regents of the University of California
    COMPANY: {<BY>? <NN> <NNP> <OF> <NN> <UNI> <OF> <COMPANY|NAME|NAME-EMAIL><COMP>?}        #130

   # Free Software Foundation, Inc.
    COMPANY: {<NN|NNP> <NNP> <COMP> <COMP>}       #135

   #  Mediatrix Telecom, inc. <ericb@mediatrix.com>
    COMPANY: {<NNP>+ <COMP> <EMAIL>}       #136

   # Corporation/COMP for/NN  National/NNP Research/COMP Initiatives/NNP
    COMPANY: {<COMP> <NN> <NNP> <COMP> <NNP>}       #140

    # Sun Microsystems, Inc. Mountain View
    COMPANY: {<COMP> <COMP> <NNP><NNP>}       #144
    # AT&T Laboratories, Cambridge
    COMPANY: {<COMP> <COMP> <NNP>}       #145

    # rare "Software in the public interest, Inc."
    COMPANY: {<COMP> <CD> <COMP>}        #170
    COMPANY: {<NNP> <IN><NN> <NNP> <NNP>+<COMP>?}        #180

    # Commonwealth Scientific and Industrial Research Organisation (CSIRO)
    COMPANY: {<NNP> <NNP> <CC> <NNP> <COMP> <NNP> <CAPS>}

    COMPANY: {<NNP> <CC> <NNP> <COMP> <NNP>*}        #200

    # Android Open Source Project, 3Dfx Interactive, Inc.
    COMPANY: {<NN>? <NN> <NNP> <COMP>}        #205

    NAME: {<NNP> <NNP> <COMP> <CONTRIBUTORS> <URL|URL2>} #206

    # Thai Open Source Software Center Ltd
    # NNP  NN   NNP    NNP      COMP   COMP')
    COMPANY: {<NNP> <NN> <NNP> <NNP> <COMP>+} #207

    #  Massachusetts Institute of Technology
    COMPANY: {<NNP> <COMP|COMPANY> <OF> <NNP>+}        #208

    COMPANY: {<NNP|CAPS>+ <COMP|COMPANY>+}        #210

    # University of Southern California, Information Sciences Institute (ISI)
    COMPANY: {<UNI> <OF> <COMPANY> <CAPS>?}        #211

    COMPANY: {<UNI|NNP> <VAN|OF> <NNP>+ <UNI>?}        #220
    COMPANY: {<NNP>+ <UNI>}        #230
    COMPANY: {<UNI> <OF> <NN|NNP>}        #240
    COMPANY: {<COMPANY> <CC> <COMPANY>}        #250

    # University of Southern California, Information Sciences Institute (ISI)
    COMPANY: {<COMPANY> <COMPANY> <CAPS>} #251

    # University of Technology
    COMPANY: {<UNI>  <OF>  <COMP|COMPANY>} #252

    # GNOME i18n Project for Vietnamese
    COMPANY: {<CAPS> <NN> <COMP> <NN> <NNP>} #253

    COMPANY: {<CAPS> <NN> <COMP>}        #255

    # Project contributors
    COMPANY: {<COMP> <CONTRIBUTORS>}   #256

    COMPANY: {<COMP>+}        #260

    # Nokia Corporation and/or its subsidiary(-ies)
    COMPANY: {<COMPANY> <CC> <NN> <COMPANY>}   #265

    COMPANY: {<COMPANY> <CC> <NNP>+}        #270
    # AIRVENT SAM s.p.a - RIMINI(ITALY)
    COMPANY: {<COMPANY> <DASH> <NNP|NN> <EMAIL>?}        #290

    # Typical names
    #John Robert LoVerso
    NAME: {<NNP> <NNP> <MIXEDCAP>}        #340

    # Kaleb S. KEITHLEY
    NAME: {<NNP> <NNP> <CAPS>} #345

    # Copyright (c) 2006, Industrial Light & Magic
    NAME: {<NNP> <NNP>  <CC>  <NNP>+} #346

    # NAME-YEAR starts or ends with a YEAR range
    NAME-YEAR: {<YR-RANGE> <NNP> <NNP>+} #350

    # Academy of Motion Picture Arts
    NAME: {<NNP|PN>+ <NNP>+}        #351

    # Joe DASILVA
    NAME: {<NNP> <CAPS>} #352

    # <s> Gangadharan N </s>
    NAME: {<NNP> <PN>+} #353

    NAME: {<NNP> <NN|NNP> <EMAIL>}        #390
    NAME: {<NNP> <PN|VAN>? <PN|VAN>? <NNP>}        #400
    NAME: {<NNP> <NN> <NNP>}        #410
    NAME: {<NNP> <COMMIT>}        #420
    # the LGPL VGABios developers Team
    NAME: {<NN>? <NNP> <MAINT> <COMP>}        #440
    # Debian Qt/KDE Maintainers
    NAME: {<NNP> <NN>? <MAINT>}        #460
    NAME: {<NN>? <NNP> <CC> <NAME>}        #480
    NAME: {<NN>? <NNP> <OF> <NN>? <NNP> <NNP>?}        #490

    # Academy of Motion Picture Arts and Sciences
    NAME: {<NNP|PN>+ <CC>+ <NNP>+}        #350again

    NAME: {<NAME> <CC> <NAME>}        #500

    COMPANY: {<NNP> <IN> <NN>? <COMPANY>}        #510

    # and Josh MacDonald.
    NAME: {<CC> <NNP> <MIXEDCAP>}        #480

    NAME: {<NAME> <UNI>}        #483

    # Kungliga Tekniska Hogskolan (Royal Institute of Technology, Stockholm, Sweden)
    COMPANY: {<COMPANY> <OF> <COMPANY> <NAME> } #529

    # Instituto Nokia de Tecnologia
    COMPANY: {<COMPANY> <NNP> <OF> <COMPANY>} #    5391

    # Laboratoire MASI - Institut Blaise Pascal
    COMPANY: {<COMPANY> <CAPS> <DASH> <COMPANY> <NAME>} #5292

    # Nara Institute of Science and Technology.
    COMPANY: {<COMPANY> <OF> <NNP> <CC> <COMPANY> } #5293

    # Instituto Nokia de Tecnologia - INdT
    COMPANY: {<COMPANY>  <NNP>  <VAN>  <COMPANY>}    #52934

    # Name 2 has a trailing email
    NAME-EMAIL: {<NAME> <EMAIL>}        #530

    # Project Mayo.
    NAME-YEAR: {<YR-RANGE> <NAME-EMAIL|COMPANY>+ <NNP>?}        #535

    NAME-YEAR: {<YR-RANGE> <NAME-EMAIL|COMPANY>+ <CC> <YR-RANGE>}        #540

    NAME: {<NAME|NAME-EMAIL>+ <OF> <NNP> <OF> <NN>? <COMPANY>}        #550
    NAME: {<NAME|NAME-EMAIL>+ <CC|OF>? <NAME|NAME-EMAIL|COMPANY>}        #560

    NAME: {<NNP><NNP>}        #5611

    # strip Software from Copyright (c) Ian Darwin 1995. Software
    NAME-YEAR: {<NAME>+ <YR-RANGE>}        #5611

    NAME-YEAR: {<YR-RANGE> <NNP>+ <CAPS>?} #5612

    #Academy of Motion Picture Arts and Sciences
    NAME: {<NAME> <CC> <NNP>} # 561

    # Adam Weinberger and the GNOME Foundation
    NAME: {<CC> <NN> <COMPANY>} # 565

    # (c) 1991-1992, Thomas G. Lane , Part of the Independent JPEG Group's
    NAME: {<PORTIONS> <OF> <NN> <NAME>+} #566

    NAME-YEAR: {<YR-RANGE> <NAME>+ <CONTRIBUTORS>?}        #570

    #also accept trailing email and URLs
    NAME-YEAR: {<NAME-YEAR> <EMAIL>?<URL>?}        #5701
    NAME-YEAR: {<NAME-YEAR>+}        #5702

    NAME: {<NNP> <OF> <NNP>}        #580
    NAME: {<NAME> <NNP>}        #590
    NAME: {<NN|NNP|CAPS>+ <CC> <OTH>}        #600
    NAME: {<NNP> <CAPS>}        #610
    NAME: {<CAPS> <DASH>? <NNP|NAME>}        #620
    NAME: {<NNP> <CD> <NNP>}        #630
    NAME: {<COMP> <NAME>+}        #640

    # Copyright 2018-2019 @paritytech/substrate-light-ui authors & contributors
    # and other contributors
    NAME: {<AUTHS>? <CC> <NN>? <CONTRIBUTORS>}        #644

    NAME: {<NNP|CAPS>+ <AUTHS|AUTHDOT|CONTRIBUTORS>}        #660

    NAME: {<VAN|OF> <NAME>}        #680
    NAME: {<NAME-YEAR> <COMP|COMPANY>}        #690
    # more names
    NAME: {<NNP> <NAME>}        #710
    NAME: {<CC>? <IN> <NAME|NNP>}        #720
    NAME: {<NAME><UNI>}        #730
    NAME: {<NAME> <IN> <NNP> <CC|IN>+ <NNP>}        #740
    # by BitRouter <www.BitRouter.com>
    NAME: {<BY> <NNP> <URL>}        #741

    # Philippe http//nexb.com joe@nexb.com
    NAME: {<NNP> <URL> <EMAIL>}        #742

    # Companies
    COMPANY: {<NAME|NAME-EMAIL|NAME-YEAR|NNP>+ <OF> <NN>? <COMPANY|COMP> <NNP>?}        #770
    COMPANY: {<NNP> <COMP|COMPANY> <COMP|COMPANY>}        #780
    COMPANY: {<NN>? <COMPANY|NAME|NAME-EMAIL> <CC> <COMPANY|NAME|NAME-EMAIL>}        #790
    COMPANY: {<COMP|COMPANY|NNP> <NN> <COMPANY|COMPANY> <NNP>+}        #800

    # by the Institute of Electrical and Electronics Engineers, Inc.
    COMPANY: {<BY> <NN> <COMPANY> <OF> <NNP> <CC> <COMPANY>}
    COMPANY: {<COMPANY> <CC> <AUTH|CONTRIBUTORS|AUTHS>}        #810

    COMPANY: {<NN> <COMP|COMPANY>+}        #820

    # this is catching a wide net by teating any bare URL as a company
    COMPANY: {<URL|URL2>}        #830

    COMPANY: {<COMPANY> <COMP|COMPANY>}        #840

    # the Software and Component Technologies group of Trimble Navigation, Ltd.
    COMPANY: {<COMPANY> <OF> <COMP|COMPANY>}        #840.1

    # University Corporation for Advanced Internet Development, Inc.
    COMPANY: {<UNI> <COMPANY>}        #845

    # The Regents of the University of California
    NAME: {<NN> <NNP> <OF> <NN> <COMPANY>}        #870

    # Trailing Authors
    COMPANY: {<NAME|NAME-EMAIL|NNP>+ <CONTRIBUTORS>}        #900

    # Jeffrey C. Foo
    COMPANY: {<PN> <COMP|COMPANY>}        #910

    # "And" some name
    ANDCO: {<CC> <NNP> <NNP>+}        #930
    ANDCO: {<CC> <OTH>}        #940
    ANDCO: {<CC> <NN> <NAME>+}        #950

    # Copyright 2005-2007 <s>Christopher Montgomery</s>, <s>Jean-Marc Valin</s>,
    # <s>Timothy Terriberry</s>, <s>CSIRO</s>, and other contributors
    ANDCO: {<CC> <CAPS|COMPANY|NAME|NAME-EMAIL|NAME-YEAR>+}          #960

    COMPANY: {<COMPANY|NAME|NAME-EMAIL|NAME-YEAR> <ANDCO>+}     #970

    # de Nemours and Company
    NAME: {<VAN>? <NNP> <ANDCO>+}                             #980

    NAME: {<BY> <NN> <AUTH|CONTRIBUTORS|AUTHS>}        #1000

    # NetGroup, Politecnico di Torino (Italy)
    # Chinese Service Center for Scholarly Exchange
    COMPANY: {<NNP> <COMPANY> <NN|NNP> <NAME>?}        #1030

    # Arizona Board of Regents (University of Arizona)
    NAME: {<COMPANY> <OF> <NN|NNP>}        #1060

    # The Regents of the University of California
    NAME: {<NAME> <COMPANY>}        #1090

    # John Doe and Myriam Doe
    NAME: {<NAME|NNP> <CC> <NNP|NAME>}        #1120

    # International Business Machines Corporation and others
    COMPANY: {<COMPANY> <CC> <OTH>}        #1150
    COMPANY: {<NAME-YEAR> <CC> <OTH>}        #1160

    # Nara Institute of Science and Technology.
    COMPANY: {<NNP> <COMPANY> <CC> <COMP>}        #1190

    # Commonwealth Scientific and Industrial Research Organisation (CSIRO)
    COMPANY: {<NNP> <COMPANY> <NAME>}        #1220

    # (The) Android Open Source Project
    COMPANY: {<NN><NN><NN>? <COMPANY>}        #1250

    # Bio++ Development Team
    COMPANY: {<NN> <NNP> <COMPANY>}        #1251

    # Institut en recherche ....
    COMPANY: {<NNP> <IN> <NN>+ <COMPANY>}        #1310

    #  OU OISTE Foundation
    COMPANY: {<OU> <COMPANY>}        #1340

    # MIT, W3C, NETLABS Temple University
    COMPANY: {<CAPS>+ <COMPANY>}        #1370

    # XZY emails
    COMPANY: {<COMPANY> <EMAIL>+}        #1400

    # by the a href http wtforms.simplecodes.com WTForms Team
    COMPANY: {<BY> <NN>+ <COMP|COMPANY>}        #1420

    # the Regents of the University of California, Sun Microsystems, Inc., Scriptics Corporation
    COMPANY: {<NN> <NNP> <OF> <NN> <UNI> <OF> <COMPANY>+}

    # Copyright (c) 1998-2000 University College London
    COMPANY: {<UNI> <UNI> <NNP>}

    # "And" some name
    ANDCO: {<CC>+ <NN> <NNP>+<UNI|COMP>?}        #1430
    ANDCO: {<CC>+ <NNP> <NNP>+<UNI|COMP>?}        #1440
    ANDCO: {<CC>+ <COMPANY|NAME|NAME-EMAIL|NAME-YEAR>+<UNI|COMP>?}        #1450
    COMPANY: {<COMPANY|NAME|NAME-EMAIL|NAME-YEAR> <ANDCO>+}        #1460

    COMPANY: {<COMPANY><COMPANY>+}        #1480

    # Copyright (c) 2002 World Wide Web Consortium, (Massachusetts Institute of
    # Technology, Institut National de Recherche en Informatique et en Automatique, Keio University).
    COMPANY: {<CC> <IN> <COMPANY>}       #1490

    # Oracle and/or its affiliates.
    NAME: {<NNP> <ANDCO>}        #1410

    # the University of California, Berkeley and its contributors.
    COMPANY: {<COMPANY> <CC> <NN> <CONTRIBUTORS>} #1411

    # UC Berkeley and its contributors
    NAME: {<NAME> <CC> <NN> <CONTRIBUTORS>} #1412

    # copyrighted by Douglas C. Schmidt and his research group at Washington University,
    # University of California, Irvine, and Vanderbilt University, Copyright (c) 1993-2008,
    COMPANY: {<NAME> <CC> <NN> <COMPANY>+} #1413

    # The University of Utah and the Regents of the University of California
    COMPANY: {<NN> <COMPANY> <CC> <NN> <COMPANY>}      #1414

    # by the Massachusetts Institute of Technology
    COMPANY: {<BY> <COMPANY> <OF> <COMPANY>}  #1415

    # Computer Systems and Communication Lab, Institute of Information Science, Academia Sinica.
    COMPANY: {<NNP> <COMPANY> <OF> <COMPANY> <NNP>} #1416

    # Copyright 2007-2010 the original author or authors.
    # Copyright (c) 2007-2010 the original author or authors.
    NAME: {<NN> <NN> <AUTH|CONTRIBUTORS|AUTHS> <NN> <AUTH|CONTRIBUTORS|AUTHS|AUTH|AUTHDOT>}        #1960

    # Copyright (C) <s>Suresh P <suresh@ippimail.com></s> #19601
    NAME: {<NNP> <PN> <EMAIL>}

    # Copyright or Copr. Mines Paristech, France - Mark NOBLE, Alexandrine GESRET
    NAME: {<NAME> <DASH> <NAME> <CAPS>} #19601

#######################################
# VARIOUS FORMS OF COPYRIGHT
#######################################

    COPYRIGHT: {<COPY> <NAME> <COPY> <YR-RANGE>}        #1510

    COPYRIGHT: {<COPY>+ <BY>? <COMPANY|NAME*|YR-RANGE>* <BY>? <EMAIL>+}        #1530

    COPYRIGHT: {<COPY>+ <NAME|NAME-EMAIL|NAME-YEAR> <CAPS> <YR-RANGE>}        #1550

    #Copyright . 2008 Mycom Pany, inc.
    COPYRIGHT: {<COPY>+ <NN> <NAME-YEAR>}        #1560

    # Copyright (c) 1995-2008 Software in the Public Interest
    COPYRIGHT: {<COPY>+  <NAME-YEAR> <IN> <NN><NN> <NNP>} #1562

    # GeSHi (C) 2004 - 2007 Nigel McNie, MyCo Inc.
    COPYRIGHT: {<NNP> <COPY>+  <NAME-YEAR> <COMPANY>+}        #1565

    # Copyright (c) 2013-2015 Streams Standard Reference Implementation Authors
    COPYRIGHT: {<COPY>+ <NAME-YEAR> <NN|NNP>+ <AUTHS>}    #1566

    # Copyright (c) Ian F. Darwin 1986, 1987, 1989, 1990, 1991, 1992, 1994, 1995.
    COPYRIGHT: {<COPY>+ <NAME|NAME-EMAIL|NAME-YEAR>+ <YR-RANGE>*}        #157999

    COPYRIGHT: {<COPY>+ <CAPS|NNP>+ <CC> <NN> <COPY> <YR-RANGE>?}        #1590

    COPYRIGHT: {<COPY>+ <BY>? <COMPANY|NAME*|NAME-EMAIL*>+ <YR-RANGE>*}        #1610

    COPYRIGHT: {<NNP>? <COPY>+ (<YR-RANGE>+ <BY>? <NN>? <COMPANY|NAME|NAME-EMAIL>+ <EMAIL>?)+}        #1630

    COPYRIGHT: {<COPY>+ <NN> <NAME> <YR-RANGE>}        #1650

    COPYRIGHT: {<COPY>+ <BY> <NAME|NAME-EMAIL|NAME-YEAR>+}        #1670

    COPYRIGHT: {<COPY> <COPY> <COMP>+}        #1690

    COPYRIGHT: {<COPY> <COPY> <NN>+ <COMPANY|NAME|NAME-EMAIL>+}        #1710

    COPYRIGHT: {<COPY>+ <NN> <NN>? <COMP> <YR-RANGE>?}        #1730

    COPYRIGHT: {<COPY>+ <NN> <NN>? <COMP> <YR-RANGE>?}        #1750
    COPYRIGHT: {<COPY> <NN> <NN>? <COMPANY> <YR-RANGE>?}        #1760

    COPYRIGHT: {<COPY>+ <YR-RANGE|NNP> <CAPS|BY>? <NNP|YR-RANGE|NAME>+}        #1780

    COPYRIGHT: {<COPY> <COPY> <NNP>+}        #1800

    # Copyright (c) 2003+ Evgeniy Polyakov <johnpol@2ka.mxt.ru>
    COPYRIGHT: {<COPY> <COPY> <YR-PLUS> <NAME|NAME-EMAIL|NAME-YEAR>+}        #1801

    # Copyright (c) 2016 Project Admins foobar
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE>+ <COMP> <NNP> <NN>}        #1830

    # Copyright (c) 1995, 1996 The President and Fellows of Harvard University
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NN> <NNP> <ANDCO>}        #1860

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NN> <AUTH|CONTRIBUTORS|AUTHS>}        #1880

    # Copyright 1999, 2000 - D.T.Shield.
    # Copyright (c) 1999, 2000 - D.T.Shield.
    COPYRIGHT2: {<COPY>+ <YR-RANGE> <DASH> <NN>}        #1920

    #(c) 2017 The Chromium Authors
    COPYRIGHT2: {<COPY>+ <YR-RANGE> <NN> <NNP> <NN>}        #1990

    # Copyright (C) Research In Motion Limited 2010. All rights reserved.
    COPYRIGHT2: {<COPYRIGHT> <COMPANY> <YR-RANGE>}        #2020

    #  Copyright (c) 1999 Computer Systems and Communication Lab,
    #                    Institute of Information Science, Academia Sinica.
    COPYRIGHT2: {<COPYRIGHT> <COMPANY> <COMPANY>}        #2060

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <BY> <NN> <NN> <NAME>}        #2080
    COPYRIGHT2: {<COPY> <YR-RANGE> <BY> <NN> <NN> <NAME>}        #2090

    COPYRIGHT2: {<COPY> <COPY><NN>? <COPY> <YR-RANGE> <BY> <NN>}        #2110

    # Copyright (c) 1992-2002 by P.J. Plauger.
    COPYRIGHT2: {<COPY> <NN>? <COPY> <YR-RANGE> <BY> <NN> <NNP>?}        #2115

    COPYRIGHT2: {<COPY>+ <NN> <YR-RANGE> <BY> <NAME>}        #2140

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <DASH> <BY>? <NAME-EMAIL|NAME>}        #2160

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <NNP> <NAME>}        #2180

    # Copyright (c) 2012-2016, Project contributors
    COPYRIGHT2: {<COPY>+ <YR-RANGE> <COMP> <AUTHS|CONTRIBUTORS>}        #2210

    COPYRIGHT2: {<COPY>+ <YR-RANGE> <COMP>}        #2230
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE>+ <CAPS>? <MIXEDCAP>}        #2240

    COPYRIGHT2: {<NAME> <COPY> <YR-RANGE>}        #2260

    # Copyright 2008 TJ <linux@tjworld.net>
    COPYRIGHT2: {<COPY> <YR-RANGE> <CAPS> <EMAIL>} #2270

    # (c) Copyright 1985-1999 SOME TECHNOLOGY SYSTEMS
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <CAPS> <CAPS> <CAPS>? <CAPS>?} #2271

    # NAME-COPY is a name with a trailing copyright
    # Daisy (c) 1998
    NAME-COPY: {<NNP> <COPY>} #2272
    COPYRIGHT2: {<NAME-COPY> <YR-RANGE>}  #2273

    # Scilab (c)INRIA-ENPC.
    COPYRIGHT: {<NAME-COPY> <NNP>} #2274

    # Copyright 1994-2007 (c) RealNetworks, Inc.
    COPYRIGHT: {<COPY>+ <YR-RANGE> <COPYRIGHT>} #2274

    # Copyright (c) 2017 Contributors et.al.
    COPYRIGHT: {<COPY> <COPY> <YR-RANGE> <CONTRIBUTORS> <OTH> } #2276

    #Copyright (c) 2020 Contributors as noted in the AUTHORS file
    COPYRIGHT: {<COPY> <COPY> <YR-RANGE> <CONTRIBUTORS> <NN>* <IN>? <NN>* <CAPS|AUTHS|ATH> <JUNK> }

    # copyrighted by Object Computing, Inc., St. Louis Missouri, Copyright (C) 2002, all rights reserved.
    COPYRIGHT: {<COPYRIGHT> <COPY>+  <YR-RANGE> <ALLRIGHTRESERVED>} #2278

    # copyrighted by Object Computing, Inc., St. Louis Missouri, Copyright (C) 2002, all rights reserved.
    COPYRIGHT: {<COPYRIGHT> <COPY>+  <YR-RANGE> <ALLRIGHTRESERVED>} #2279

    # Copyright (c) 2004, The Codehaus
    COPYRIGHT: {<COPY>  <COPY>  <YR-RANGE>  <NN>  <NNP>} #22790

    # Copyright (c) 2015, Contributors
    COPYRIGHT: {<COPY>+  <YR-RANGE>  <CONTRIBUTORS> <ALLRIGHTRESERVED>?} #22791

    # Copyright 1996, 1997 Linux International.
    COPYRIGHT: {<COPY>+  <YR-RANGE>  <NN>  <NNP>} #22792

    # Copyright (c) 2017 odahcam
    # or Copyright (c) 2019-2021, Open source contributors.
    COPYRIGHT: {<COPY>+  <YR-RANGE>  <NN>+ <CONTRIBUTORS>? <ALLRIGHTRESERVED>?} #22793

    # Licensed material of Foobar Company, All Rights Reserved, (C) 2005
    COPYRIGHT: {<COMPANY>  <ALLRIGHTRESERVED>  <COPYRIGHT>} #22794

    COPYRIGHT2: {<COPY>+ <NN|CAPS>? <YR-RANGE>+ <PN>*}        #2280

    COPYRIGHT2: {<COPY>+ <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <COMPANY>?}        #2300

    # Copyright (c) 2014, 2015, the respective contributors All rights reserved.
    COPYRIGHT: {<COPYRIGHT|COPYRIGHT2>  <NN|NNP|CONTRIBUTORS>+  <ALLRIGHTRESERVED>} #2862

    COPYRIGHT2: {<COPY>+ <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <DASH> <COMPANY>}        #2320

    COPYRIGHT2: {<NNP|NAME|COMPANY> <COPYRIGHT2>}        #2340

    COPYRIGHT: {<COPYRIGHT> <NN> <COMPANY>}        #2360

    COPYRIGHT: {<COPY>+ <BY>? <NN> <COMPANY>}        #2380

    COPYRIGHT: {<COMPANY> <NN> <NAME> <COPYRIGHT2>}        #2400
    COPYRIGHT: {<COPYRIGHT2> <COMP> <COMPANY>}        #2410

    COPYRIGHT: {<COPYRIGHT2> <NNP> <CC> <COMPANY>}        #2430

    COPYRIGHT: {<COPYRIGHT2> <NAME|NAME-EMAIL|NAME-YEAR>+}        #2860

    # Rare form Copyright (c) 2008 All rights reserved by Amalasoft Corporation.
    COPYRIGHT: {<COPYRIGHT2> <ALLRIGHTRESERVED> <BY> <COMPANY>}        #2861

    # Copyright (c) 1996 Adrian Rodriguez (adrian@franklins-tower.rutgers.edu) Laboratory for Computer Science Research Computing Facility
    COPYRIGHT: {<COPYRIGHT> <NAME>} #2400

    # copyrights in the style of Scilab/INRIA
    COPYRIGHT: {<NNP> <NN> <COPY> <NNP>}        #2460
    COPYRIGHT: {<NNP> <COPY> <NNP>}        #2470

    # Copyright or Copr. 2006 INRIA - CIRAD - INRA
    COPYRIGHT: {<COPY> <NN> <COPY> <YR-RANGE>+ <COMPANY>+}        #2500

    COPYRIGHT: {<COPYRIGHT|COPYRIGHT2> <COMPANY>+ <NAME>*}        #2580

    # iClick, Inc., software copyright (c) 1999
    COPYRIGHT: {<ANDCO> <NN>? <COPYRIGHT2>}        #2590

    # portions copyright
    COPYRIGHT: {<PORTIONS> <COPYRIGHT|COPYRIGHT2>}        #2610

    #copyright notice (3dfx Interactive, Inc. 1999), (notice is JUNK)
    COPYRIGHT: {<COPY> <JUNK> <COMPANY> <YR-RANGE>}       #2620

    # Copyright (C) <2013>, GENIVI Alliance, Inc.
    COPYRIGHT: {<COPYRIGHT2> <ANDCO>}       #2625

    #  copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.
    COPYRIGHT: {<COPY> <PN> <YR-RANGE> <BY> <COMPANY> }       #2630

    # Copyright 1996-2004, John LoVerso.
    COPYRIGHT: {<COPYRIGHT> <MIXEDCAP> }       #2632

    # Copyright (C) 1992, 1993, 1994, 1995 Remy Card (card@masi.ibp.fr) Laboratoire MASI - Institut Blaise Pascal
    COPYRIGHT: {<COPYRIGHT> <DASH> <NAME>}       #2634

    # Copyright 2002, 2003 University of Southern California, Information Sciences Institute
    COPYRIGHT: {<COPYRIGHT> <NN> <NAME>}       #2635

    # Copyright 2008 TJ <linux@tjworld.net>
    COPYRIGHT: {<COPYRIGHT2> <EMAIL>}       #2636

    # Copyright RUSS DILL Russ <Russ.Dill@asu.edu>
    COPYRIGHT: {<COPYRIGHT> <CAPS> <NAME-EMAIL>}       #2637

    # maintainer Norbert Tretkowski <nobse@debian.org> 2005-04-16
    AUTHOR: {<BY|MAINT> <NAME-EMAIL> <YR-RANGE>?}  #26382

    # Russ Dill <Russ.Dill@asu.edu> 2001-2003
    COPYRIGHT: {<NAME-EMAIL> <YR-RANGE>}       #2638

    # (C) 2001-2009, <s>Takuo KITAME, Bart Martens, and  Canonical, LTD</s>
    COPYRIGHT: {<COPYRIGHT> <NNP> <COMPANY>}       #26381

    #Copyright (c) 1995, 1996 - Blue Sky Software Corp.
    COPYRIGHT: {<COPYRIGHT2> <DASH> <COMPANY>}       #2639

    #copyright 2000-2003 Ximian, Inc. , 2003 Gergo Erdi
    COPYRIGHT: {<COPYRIGHT> <NNP> <NAME-YEAR>}        #1565

    #2004+ Copyright (c) Evgeniy Polyakov <zbr@ioremap.net>
    COPYRIGHT: {<YR-PLUS> <COPYRIGHT>}        #1566

    # Copyright (c) 1992 David Giller, rafetmad@oxy.edu 1994, 1995 Eberhard Moenkeberg, emoenke@gwdg.de 1996 David van Leeuwen, david@tm.tno.nl
    COPYRIGHT: {<COPYRIGHT> <EMAIL>}        #2000

    COPYRIGHT: {<COPYRIGHT> <NAME|NAME-YEAR>+}        #2001

    # copyright by M.I.T. or by MIT
    COPYRIGHT: {<COPY> <BY> <NNP|CAPS>}        #2002

    # Copyright property of CompuServe Incorporated.
    COPYRIGHT: {<COPY> <NN> <OF> <COMPANY>}        #2003

    # Copyright (c) 2005 DMTF.
    COPYRIGHT: {<COPY> <YR-RANGE> <PN>}        #2004

    # Copyright (c) YEAR This_file_is_part_of_KDE
    COPYRIGHT: {<COPY> <COPY> <CAPS>}        #2005

    # copyrighted by the Free Software Foundation
    COPYRIGHT: {<COPY> <BY> <NN>? <NNP>? <COMPANY>}        #2006

    # copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc
    COPYRIGHT: {<COPY> <PN>?  <YR-RANGE> <BY> <NN> <NAME>}   #2007

    # Copyright (C) 2005 SUSE Linux Products GmbH.
    COPYRIGHT: {<COPYRIGHT2> <CAPS> <NN> <COMPANY>} #2008

    # COPYRIGHT (c) 2006 - 2009 DIONYSOS
    COPYRIGHT: {<COPYRIGHT2> <CAPS>} #2009

    # Copyright (C) 2000 See Beyond Communications Corporation
    COPYRIGHT2: {<COPYRIGHT2> <JUNK> <COMPANY>} # 2010

    # copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.
    COPYRIGHT: {<COPY> <PN> <YR-RANGE> <COMPANY>}

    COPYRIGHT2: {<NAME-COPY> <COPYRIGHT2>}  #2274

    # (C) COPYRIGHT 2004 UNIVERSITY OF CHICAGO
    COPYRIGHT: {<COPYRIGHT2> <UNI> <OF> <CAPS>} #2276

    # NAME-CAPS is made of all caps words
    #Copyright or Copr. CNRS
    NAME-CAPS: {<CAPS>+}        #2530

    #Copyright or Copr. CNRS
    COPYRIGHT: {<COPY> <NN> <COPY> <COPYRIGHT|NAME-CAPS>}        #2560
    COPYRIGHT: {<COPYRIGHT2> <BY> <NAME-CAPS>} #2561

    # Copyright (c) 2004, The Codehaus
    COPYRIGHT: {<COPYRIGHT2> <NN> <NNP>} #2562

    # Copyright (c) 2007-2014 IOLA and Ole Laursen.
    COPYRIGHT: {<COPYRIGHT> <ANDCO>}  #2563

    # Vladimir Oleynik <dzo@simtreas.ru> (c) 2002
    COPYRIGHT: {<NAME-EMAIL> <COPYRIGHT2>}        #2840

    #copyright of CERN. or copyright CERN.
    COPYRIGHT: {<COPY> <OF>? <PN>}        #26371

    COPYRIGHT: {<NAME-EMAIL> <COPYRIGHT2>}        #2840

    COPYRIGHT: {<COPYRIGHT2> <COPY> <NN> <NNP> <ALLRIGHTRESERVED>} #3000

    # Copyright (c) World Wide Web Consortium , Massachusetts Institute of Technology ,
    # Institut National de Recherche en Informatique et en Automatique , Keio University
    COPYRIGHT: {<COPYRIGHT> <OF> <COMPANY> <NAME> <NAME> <COMPANY> } #3000

    #  Copyright (c) 1988, 1993 The Regents of the University ofCalifornia. All rights reserved.
    COPYRIGHT: {<COPYRIGHT> <OF> <NN> <UNI> <NN|OF>? <NNP>?  <ALLRIGHTRESERVED> } #3010

    # (C) Unpublished Work of Sample Group, Inc.  All Rights Reserved.
    COPYRIGHT: {<COPY>+  <NNP> <NN> <OF> <COMPANY>} #3020

    # Foobar Company, All Rights Reserved, (C) 2005
    COPYRIGHT: {<COMPANY> <ALLRIGHTRESERVED> <COPYRIGHT2>} #3030

    # Copyright (c) 2000 United States Government as represented by the Secretary of the Navy. All rights reserved.
    COPYRIGHT: {<COPYRIGHT> <NN> <NN> <NN|NNP> <BY> <NN> <NAME> <ALLRIGHTRESERVED>} #3035

    # Copyright (c) 2007-2008, Y Giridhar Appaji Nag <giridhar@appaji.net>
    COPYRIGHT: {<COPYRIGHT> <COMPANY|NAME|NAME-EMAIL|NAME-YEAR>+} #3040

    # copyright C 1988 by the Institute of Electrical and Electronics Engineers, Inc.
    COPYRIGHT: {<COPYRIGHT2> <BY> <COMPANY>} #3050

    # Copyright (c) 2007 Hiran Venugopalan , Hussain K H , Suresh P , Swathanthra Malayalam Computing
    COPYRIGHT: {<COPYRIGHT> <NAME-CAPS> <ANDCO>} #3060

    # Copyright (c) 1995-2018 The PNG Reference Library Authors
    COPYRIGHT: {<COPYRIGHT2> <NN> <NAME-CAPS> <NN> <NAME>} #3065

    # Copyright (c) 2011 The WebRTC project authors
    COPYRIGHT: {<COPY>+ <NAME-YEAR> <AUTHS>} #1567

    # Copyright (c), ALL Consulting, 2008
    COPYRIGHT: {<COPY>+ <NN> <NN>? <NNP> <YR-RANGE>} # 15675

    # Multilines
    # Copyright (c) Sebastian Classen sebastian.classen [at] freenet.ag, 2007
    # Jan Engelhardt jengelh [at] medozas de, 2007 - 2010
    COPYRIGHT: {<COPYRIGHT> <CC> <YR-RANGE>} # 15676

    # Copyright (C), 2001-2011, Omega Tech. Co., Ltd.
    # Or complex with markup as in Copyright (C) &amp;#36;today.year Google Inc.
    COPYRIGHT: {<COPY> <COPY> <ANDCO>}  #2841

    # Copyright (c) 1995-2018 The PNG Reference Library Authors. (with and without trailing dot)
    COPYRIGHT: {<COPYRIGHT> <NN> <AUTHDOT>} #35011

    ############ All right reserved in the middle ##############################

    # http//www.enox.biz/ Copyright (C) All rights Reserved by Enoxbiz
    COPYRIGHT: {<COMPANY>  <COPY>  <COPY>  <ALLRIGHTRESERVED>  <BY>  <NAME>}     #15800

    # South Baylo University Copyright (c) All Right Reserved. 2018
    COPYRIGHT: {<COMPANY>  <COPY>  <COPY>  <ALLRIGHTRESERVED> <YR-RANGE>?}      #157201

    # Crown Copyright C All rights reserved. or Crown Copyright (C) All rights reserved.
    COPYRIGHT: {<NAME-COPY> <NAME-CAPS|COPY> <ALLRIGHTRESERVED>}                #15730

    # Copyright (c) All Rights Reserved by the District Export Council of Georgia
    COPYRIGHT: {<COPY>+ <ALLRIGHTRESERVED> <BY>? <NN> <NAME> } #15674

    # Copyright (c) All right reserved SSC. Ltd.
    # Copyright (C) All Rights Reserved by Leh. www.leh.jp
    # Copyright (c) 2014-2019 New Avenue Foundation.
    COPYRIGHT: {<COPY>+ <ALLRIGHTRESERVED> <NAME|NAME-YEAR|COMPANY> } # 15680

    # Copyright (c) - All Rights Reserved - PROAIM Medical.
    COPYRIGHT: {<COPY>+ <DASH>? <ALLRIGHTRESERVED> <DASHCAPS> <NNP> } # 15690

    # Copyright(c) All rights reserved by Minds, Japan Council for Quality Health Care.
    # Copyright(c) All Rights Reserved by Chinese Service Center for Scholarly Exchange
    COPYRIGHT: {<COPY>+  <ALLRIGHTRESERVED>  <BY>  <NAME|COMPANY>  <NN>  <NAME>}  #15700

    # Copyright(c) All rights reserved by IBM Corp.
    COPYRIGHT: {<COPY>+ <ALLRIGHTRESERVED> <BY> <NAME|NAME-YEAR|COMPANY> } # 15710

    ############################################################################

    # Copyright . 2008 Mycom Pany, inc. OR Copyright . 2008 company name, inc.
    COPYRIGHT: {<COPY>  <NNP>  <NAME-YEAR> <COMPANY>?} #15720

    # Copyright (c) 2008-1010 Intel Corporation
    COPYRIGHT: {<COPY>  <COPY>  <CD>  <COMPANY>} #rare-cd-not-year

    # Copyright (C) 2005-2006  dann frazier <dannf@dannf.org>
    COPYRIGHT: {<COPYRIGHT2>  <NN>  <NN>  <EMAIL>} #999991

    # URL-like at the start
    COPYRIGHT: {<COMPANY>  <YR-RANGE>  <COPY>+  <ALLRIGHTRESERVED>} #999992

    # Copyright (c) 2008 Intel Corporation / Qualcomm Inc.
    COPYRIGHT: {<COPYRIGHT>  <DASH>  <COMPANY>} #copydash-co

    #Copyright Holders Kevin Vandersloot <kfv101@psu.edu> Erik Johnsson <zaphod@linux.nu>
    COPYRIGHT: {<COPY> <HOLDER> <NAME>}       #83000

    #holder is Tim Hudson (tjh@mincom.oz.au).
    COPYRIGHT: {<HOLDER> <JUNK> <NAME-EMAIL>}       #83001

    # Copyright lowRISC contributors.
    COPYRIGHT: {<COPY> <NN> <CONTRIBUTORS>}

#######################################
# Authors
#######################################

    # SPDX-FileContributor special case
    AUTHOR: {<SPDX-CONTRIB> <CCOMPANY|NAME|NAME-EMAIL|NAME-YEAR|EMAIL> <COMPANY|NAME|NAME-EMAIL|NAME-YEAR|EMAIL|NN>? }        #264000

    # developed by Project Mayo.
    AUTHOR: {<AUTH2>+ <BY> <COMPANY> <NNP>}        #2645-1

    # Created by XYZ
    AUTH: {<AUTH2>+ <BY>}        #2645-2

    # by  Yukihiro Matsumoto matz@netlab.co.jp.
    # AUTH: {<BY> <NAME>}        #2645-3

    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN>? <COMPANY|NAME|YR-RANGE>* <BY>? <EMAIL>+}        #2650

    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN>? <COMPANY|NAME|NAME-EMAIL|NAME-YEAR>+ <YR-RANGE>*}       #2660

    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <YR-RANGE>+ <BY>? <COMPANY|NAME|NAME-EMAIL>+}        #2670
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <YR-RANGE|NNP> <NNP|YR-RANGE>+}        #2680
    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NN|CAPS>? <YR-RANGE>+}        #2690
    AUTHOR: {<COMPANY|NAME|NAME-EMAIL>+ <AUTH|CONTRIBUTORS|AUTHS>+ <YR-RANGE>+}        #2700

    #AUTHOR: {<YR-RANGE> <NAME|NAME-EMAIL>+}        #2710
    AUTHOR: {<BY> <CC>? <NAME-EMAIL>+}        #2720

    AUTHOR: {<AUTH|CONTRIBUTORS|AUTHS>+ <NAME-EMAIL>+}        #2720
    AUTHOR: {<AUTHOR> <CC> <NN>? <AUTH|AUTHS>}        #2730
    AUTHOR: {<BY> <EMAIL>}        #2740
    ANDAUTH: {<CC> <AUTH|NAME|CONTRIBUTORS>+}        #2750
    AUTHOR: {<AUTHOR> <ANDAUTH>+}        #2760

    # developed by Mitsubishi and NTT.
    AUTHOR: {<AUTH|AUTHS|AUTH2> <BY>? <NNP> <CC> <PN>} #2761

    # developed by the National Center for Supercomputing Applications at the University of Illinois at Urbana-Champaign
    AUTHOR: {<AUTHOR> <NN> <NAME> <NAME>} #2762

    # created by Axel Metzger and Till Jaeger, Institut fur Rechtsfragen der Freien und Open Source Software
    AUTHOR: {<AUTH2> <CC> <AUTHOR> <NN> <NAME> <NN> <NN> <NNP>} #2645-4

    # developed by the XML DB Initiative http//www.xmldb.org
    AUTHOR: {<AUTH2> <COMPANY>} #2645-7

    # Author not attributable
    AUTHOR: {<AUTH>  <NN>  <NNP>} #not attributable

    # author (Panagiotis Tsirigotis)
    AUTHOR: {<AUTH>  <NNP><NNP>+} #author Foo Bar

    # Author: Tim (xtimor@gmail.com)
    AUTHOR: {<AUTH>  <NNP>+ <EMAIL>+} #Author Foo joe@email.com


#######################################
# Mixed AUTHOR and COPYRIGHT
#######################################

    # Compounded statements usings authors

    # Copyright by Daniel K. Gebhart
    # Also found in some rare cases with a long list of authors.
    COPYRIGHT: {<COPY> <BY>? <AUTHOR>+  <YR-RANGE>*}        #2800-1

    COPYRIGHT: {<AUTHOR> <COPYRIGHT2>}        #2820
    COPYRIGHT: {<AUTHOR> <YR-RANGE>}        #2830
    # copyrighted by MIT
    COPYRIGHT: {<COPY> <BY> <MIT>} #2840

    # Copyright (c) 1995-2018 The PNG Reference Library Authors
    COPYRIGHT: {<COPYRIGHT2> <NN> <NAME-CAPS> <NN> <NN> <AUTHS>} #3000

    # COPYRIGHT Written by John Cunningham Bowler, 2015.
    COPYRIGHT: {<COPY> <AUTHOR>} #4000

    # Created by Samvel Khalatyan, May 28, 2013 Copyright 2013, All rights reserved
    COPYRIGHT: {<AUTHOR> <NN>  <YR-RANGE>  <COPYRIGHT2>  <ALLRIGHTRESERVED>} #4200


#######################################
# Last resort catch all ending with ALLRIGHTRESERVED
#######################################

    COPYRIGHT: {<COMPANY><COPY>+<ALLRIGHTRESERVED>}        #99900

    COPYRIGHT: {<COPYRIGHT|COPYRIGHT2|COPY|NAME-COPY> <COPY|NNP|AUTHDOT|CAPS|CD|YR-RANGE|NAME|NAME-EMAIL|NAME-YEAR|NAME-COPY|NAME-CAPS|AUTHORANDCO|COMPANY|YEAR|PN|COMP|UNI|CC|OF|IN|BY|OTH|VAN|URL|EMAIL|URL2|MIXEDCAP|NN>+ <ALLRIGHTRESERVED>}        #99999

    COPYRIGHT: {<COPY|NAME-COPY><COPY|NAME-COPY>}        #999990
    COPYRIGHT: {<COPYRIGHT|COPYRIGHT2> <ALLRIGHTRESERVED>}        #99900111

"""

################################################################################
# MAIN CLEANUP ENTRY POINTS
################################################################################


def refine_copyright(c):
    """
    Refine a detected copyright string.
    FIXME: the grammar should not allow this to happen.
    """
    if not c:
        return
    c = ' '.join(c.split())
    c = strip_some_punct(c)
    # this catches trailing slashes in URL for consistency
    c = c.strip('/ ')
    c = strip_all_unbalanced_parens(c)
    c = remove_same_extra_words(c)
    c = ' '.join(c.split())
    c = remove_dupe_copyright_words(c)
    c = strip_prefixes(c, prefixes=set(['by', 'c']))
    c = c.strip()
    c = c.strip('+')
    c = strip_balanced_edge_parens(c)
    c = strip_suffixes(c, suffixes=COPYRIGHTS_SUFFIXES)
    c = strip_trailing_period(c)
    c = c.strip("'")
    return c.strip()


def refine_holder(h):
    """
    Refine a detected holder.
    FIXME: the grammar should not allow this to happen.
    """
    if not h:
        return
    # handle the acse where "all right reserved" is in the middle and the
    # company name contains the word all.
    if 'reserved' in h.lower():
        prefixes = HOLDERS_PREFIXES_WITH_ALL
    else:
        prefixes = HOLDERS_PREFIXES
    h = refine_names(h, prefixes=prefixes)
    h = strip_suffixes(h, HOLDERS_SUFFIXES)
    h = h.strip()
    h = h.strip('+')
    h = h.replace('( ', ' ').replace(' )', ' ')
    h = h.strip()
    h = strip_trailing_period(h)
    h = h.strip()
    if h and h.lower() not in HOLDERS_JUNK:
        return h


def refine_author(a):
    """
    Refine a detected author.
    FIXME: the grammar should not allow this to happen.
    """
    if not a:
        return
    # FIXME: we could consider to split comma separated lists such as
    # gthomas, sorin@netappi.com, andrew.lunn@ascom.che.g.
    a = refine_names(a, prefixes=AUTHORS_PREFIXES)
    a = a.strip()
    a = strip_trailing_period(a)
    a = a.strip()
    a = strip_balanced_edge_parens(a)
    a = a.strip()
    a = refine_names(a, prefixes=AUTHORS_PREFIXES)
    a = a.strip()
    if a and a.lower() not in AUTHORS_JUNK:
        return a


def refine_names(s, prefixes):
    """
    Refine a detected name (author, hodler).
    FIXME: the grammar should not allow this to happen.
    """
    s = strip_some_punct(s)
    s = strip_leading_numbers(s)
    s = strip_all_unbalanced_parens(s)
    s = strip_some_punct(s)
    s = s.strip()
    s = strip_balanced_edge_parens(s)
    s = s.strip()
    s = strip_prefixes(s, prefixes)
    s = s.strip()
    return s

################################################################################
# COPYRIGHTS CLEANUPS
################################################################################


PREFIXES = frozenset([
    '?',
    '????',
    '(insert',
    'then',
    'current',
    'year)',
    'maintained',
    'by',
    'developed',
    'created',
    'written',
    'recoded',
    'coded',
    'modified',
    'maintained'
    'created',
    '$year',
    'year',
    'uref',
    'owner',
    'from',
    'and',
    'of',
    'to',
    'for',
    'or',
    '<p>',
])

COPYRIGHTS_SUFFIXES = frozenset([
    'copyright',
    '.',
    ',',
    'year',
    'parts',
    'any',
    '0',
    '1',
    'author',
    'all',
    'some',
    'and'
])

# Set of statements that get detected and are junk/false positive
# note: this must be lowercase and be kept to a minimum.
# A junk copyright cannot be resolved otherwise by parsing with a grammar.
# It would be best not to have to resort to this, but this is practical.
COPYRIGHTS_JUNK = frozenset([
    # TODO: consider removing to report these (and this is a sign that curation is needed)
    'copyright (c)',
    '(c) by',

    "copyright holder's name",
    '(c) (c)',
    'c',
    '(c)',
    'full copyright statement',
    'copyrighted by their authors',
    'copyrighted by their authors.',
    'copyright holder or other authorized',
    'copyright holder who authorizes',
    'copyright holder has authorized',
    'copyright holder nor the author',
    'copyright holder(s) or the author(s)',
    'copyright holders and contributors',
    'copyright owner or entity authorized',
    'copyright owner or contributors',
    'copyright and license, contributing',
    'copyright for a new language file should be exclusivly the authors',
    'copyright (c) year',
    'copyright (c) year your name',

    'copyright holder or said author',
    'copyright holder, or any author',
    'copyright holder and contributor',
    'copyright-holder and its contributors',
    'copyright holders and contributors.',
    'copyright holder and contributors.',
    'copyright holders and contributors',
    'copyright holder and contributors',

    'copyrighted material, only this license, or another one contracted with the authors',
    'copyright notices, authorship',
    'copyright holder means the original author(s)',
    "copyright notice. timevar.def's author",
    'copyright copyright and',
    "copyright holder or simply that it is author-maintained'.",
    "copyright holder or simply that is author-maintained'.",
    '(c) if you bring a patent claim against any contributor',
    'copyright-check writable-files m4-check author_mark_check',
    "copyright of uc berkeley's berkeley software distribution",
    '(c) any recipient',
    '(c) each recipient',
    'copyright in section',
    'u.s. copyright act',
    # from a WROX license text
    'copyright john wiley & sons, inc. year',
    'copyright holders and contributing',
    '(c) individual use.',
    'copyright, license, and disclaimer',
    '(c) forums',
    # from the rare LATEX licenses
    'copyright 2005 m. y. name',
    'copyright 2003 m. y. name',
    'copyright 2001 m. y. name',
    'copyright. united states',
    '(c) source code',
    'copyright, designs and patents',
    '(c) software activation.',
    '(c) cockroach enterprise edition',
    'attn copyright agent',
    'code copyright grant',
    # seen in a weird Adobe license
    'copyright redistributions',
    'copyright neither',
    'copyright including, but not limited',
    'copyright not limited',
    # found in an RPM spec file COPYRIGHT: LGPL\nGROUP: ....
    'copyright lgpl group',
    'copyright gpl group',
    # from strace-4.6/debian/changelog:
    # * Add location of upstream sources to the copyright
    # * Merged ARM architecture support from Jim Studt <jim@federated.com>
    'copyright merged arm',
    # common in sqlite
    '(c) as',
#    'copyright as',
    # from libmng - libmng.spec
    # Copyright: AS IS
    # Group: System Environment/Libraries
    'copyright as is group system',

    'copyright united states',
    'copyright as is group',
    'copyrighted by its',
    'copyright',
    'copyright by',
    'copyrighted',
    'copyrighted by',
    'copyright (c) <holders>',
    'copyright (c) , and others',
    'copyright from license',
    'and/or the universal copyright convention 1971',
    'universal copyright convention',
    'copyright 2005 m. y. name',
    'copyright 2005 m. y.',
    'copyright 2003 m. y. name',
    'copyright 2003 m. y.',
    'copyright 2001 m. y. name',
    'copyright 2001 m. y.',
    'copyright help center',
])

################################################################################
# AUTHORS CLEANUPS
################################################################################

AUTHORS_PREFIXES = frozenset(set.union(
    set(PREFIXES),
    set([
        'contributor',
        'contributors',
        'contributor(s)',
        'authors',
        'author',
        'author:',
        'author(s)',
        'authored',
        'created',
        'author.',
        'author\'',
        'authors,',
        'authorship',
        'or',
        'spdx-filecontributor',
    ])
))

# Set of authors that get detected and are junk/false positive
# note: this must be lowercase and be kept to a minimum.
# A junk copyright cannot be resolved otherwise by parsing with a grammar.
# It would be best not to have to resort to this, but this is practical.
AUTHORS_JUNK = frozenset([
    # in GNU licenses
    'james hacker.',
    'james random hacker.',
    'contributor. c. a',
    'grant the u.s. government and others',
    'james random hacker',
    'james hacker',
    'company',
    'contributing project',
    'its author',
    'gnomovision',
    'would',
    'may',
    'attributions',
    'the',
])

################################################################################
# HOLDERS CLEANUPS
################################################################################

HOLDERS_PREFIXES = frozenset(set.union(
    set(PREFIXES),
    set([
        '-',
        'a',
        '<a',
        'href',
        'ou',
        'portions',
        'portion',
        'notice',
        'holders',
        'holder',
        'property',
        'parts',
        'part',
        'at',
        'cppyright',
        'assemblycopyright',
        'c',
        'works',
        'present',
        'at',
        'right',
        'rights',
        'reserved',
        'held',
        'by',
        'is',
        '(x)',
    ])
))

HOLDERS_PREFIXES_WITH_ALL = HOLDERS_PREFIXES.union(set(['all']))

HOLDERS_SUFFIXES = frozenset([
    'http',
    'and',
    'email',
    'licensing@',
    '(minizip)',
    'website',
    '(c)',
    '<http',
    '/>',
    '.',
    ',',
    'year',
    # this may truncate rare companies named "all something"
    'some',
    'all',
    'right',
    'rights',
    'reserved',
    'reserved.',
    'href',
    'c',
    'a',
])

# these final holders are ignored.
HOLDERS_JUNK = frozenset([
    'a href',
    'property',
    'licensing@',
    'c',
    'works',
    'http',
    'the',
    'are',
    '?',
    'cppyright',
    'parts',
    'disclaimed',
    'or',
    '<holders>',
    'author',
])

################################################################################
# TEXT POST PROCESSING and CLEANUP
################################################################################


def remove_dupe_copyright_words(c):
    c = c.replace('SPDX-FileCopyrightText', 'Copyright')
    # from .net assemblies
    c = c.replace('AssemblyCopyright', 'Copyright')
    c = c.replace('AppCopyright', 'Copyright')
    c = c.replace('JCOPYRIGHT', 'Copyright')
    # FIXME: this should be in the grammar, but is hard to get there right
    # these are often artifacts of markup
    c = c.replace('COPYRIGHT Copyright', 'Copyright')
    c = c.replace('Copyright Copyright', 'Copyright')
    c = c.replace('Copyright copyright', 'Copyright')
    c = c.replace('copyright copyright', 'Copyright')
    c = c.replace('copyright Copyright', 'Copyright')
    c = c.replace('copyright\'Copyright', 'Copyright')
    c = c.replace('copyright"Copyright', 'Copyright')
    c = c.replace('copyright\' Copyright', 'Copyright')
    c = c.replace('copyright" Copyright', 'Copyright')
    return c


def remove_same_extra_words(c):
    c = c.replace('<p>', ' ')
    c = c.replace('<a href', ' ')
    c = c.replace('date-of-software', ' ')
    c = c.replace('date-of-document', ' ')
    c = c.replace(' $ ', ' ')
    c = c.replace(' ? ', ' ')
    c = c.replace('</a>', ' ')
    c = c.replace('( )', ' ')
    c = c.replace('()', ' ')
    return c


def strip_prefixes(s, prefixes=()):
    """
    Return the `s` string with any of the string in the `prefixes` set
    striped. Normalize and strip spacing.
    """
    s = s.split()
    # strip prefixes.
    # NOTE: prefixes are hard to catch otherwise, unless we split the
    # author vs copyright grammar in two
    while s and s[0].lower() in prefixes:
        s = s[1:]
    s = ' '.join(s)
    return s


def strip_suffixes(s, suffixes=()):
    """
    Return the `s` string with any of the string in the `suffixes` set
    striped. Normalize and strip spacing.
    """
    s = s.split()
    while s and s[-1].lower() in suffixes:
        s = s[:-1]
    s = ' '.join(s)
    return s


def strip_trailing_period(s):
    """
    Return the `s` string with trailing periods removed when needed.
    """
    if not s:
        return s

    s = s.strip()

    if not s.endswith('.'):
        return s

    if len(s) < 3 :
        return s

    is_single_word = len(s.split()) == 1

    if s[-2].isupper() and not is_single_word:
        # U.S.A., e.V., M.I.T. and similar
        return s

    if s[-3] == '.':
        # S.A., e.v., b.v. and other
        return s

    if s.lower().endswith(('inc.', 'corp.', 'ltd.', 'llc.', 'co.', 'llp.')):
        return s

    return s.rstrip('.')


def refine_date(c):
    """
    Refine a detected date or date range.
    FIXME: the grammar should not allow this to happen.
    """
    return strip_some_punct(c)


def strip_leading_numbers(s):
    """
    Return a string removing leading words made only of digits.
    """
    s = s.split()
    while s and s[0].isdigit():
        s = s[1:]
    return ' '.join(s)


def strip_some_punct(s):
    """
    Return a string stripped from some leading and trailing punctuations.
    """
    if s:
        s = s.strip(''','"}{-_:;&@!''')
        s = s.lstrip('.>)]\\/')
        s = s.rstrip('<([\\/')
    return s


def fix_trailing_space_dot(s):
    """
    Return a string stripped from some leading and trailing punctuations.
    """
    if s and s.endswith(' .'):
        s = s[:-2] + '.'
    return s


def strip_unbalanced_parens(s, parens='()'):
    """
    Return a string where unbalanced parenthesis are replaced with a space.
    `paren` is a pair of characters to balance  such as (), <>, [], {}.

    For instance:
    >>> strip_unbalanced_parens('This is a super string', '()')
    'This is a super string'

    >>> strip_unbalanced_parens('This is a super(c) string', '()')
    'This is a super(c) string'

    >>> strip_unbalanced_parens('This ((is a super(c) string))', '()')
    'This ((is a super(c) string))'

    >>> strip_unbalanced_parens('This )(is a super(c) string)(', '()')
    'This  (is a super(c) string) '

    >>> strip_unbalanced_parens('This )(is a super(c) string)(', '()')
    'This  (is a super(c) string) '

    >>> strip_unbalanced_parens('This )(is a super(c) string)(', '()')
    'This  (is a super(c) string) '

    >>> strip_unbalanced_parens('This )((is a super(c) string)((', '()')
    'This   (is a super(c) string)  '

    >>> strip_unbalanced_parens('This ) is', '()')
    'This   is'

    >>> strip_unbalanced_parens('This ( is', '()')
    'This   is'

    >>> strip_unbalanced_parens('This )) is', '()')
    'This    is'

    >>> strip_unbalanced_parens('This (( is', '()')
    'This    is'

    >>> strip_unbalanced_parens('(', '()')
    ' '

    >>> strip_unbalanced_parens(')', '()')
    ' '
    """
    start, end = parens
    if not start in s and not end in s:
        return s

    unbalanced = []
    unbalanced_append = unbalanced.append

    stack = []
    stack_append = stack.append
    stack_pop = stack.pop

    for i, c in enumerate(s):
        if c == start:
            stack_append((i, c,))
        elif c == end:
            try:
                stack_pop()
            except IndexError:
                unbalanced_append((i, c,))

    unbalanced.extend(stack)
    pos_to_del = set([i for i, c in unbalanced])
    cleaned = [c if i not in pos_to_del else ' ' for i, c in enumerate(s)]
    return type(s)('').join(cleaned)


def strip_all_unbalanced_parens(s):
    """
    Return a string where unbalanced parenthesis are replaced with a space.
    Strips (), <>, [] and {}.
    """
    c = strip_unbalanced_parens(s, '()')
    c = strip_unbalanced_parens(c, '<>')
    c = strip_unbalanced_parens(c, '[]')
    c = strip_unbalanced_parens(c, '{}')
    return c


def strip_balanced_edge_parens(s):
    """
    Return a string where a pair of balanced leading and trailing parenthesis is
    stripped.

    For instance:
    >>> strip_balanced_edge_parens('(This is a super string)')
    'This is a super string'
    >>> strip_balanced_edge_parens('(This is a super string')
    '(This is a super string'
    >>> strip_balanced_edge_parens('This is a super string)')
    'This is a super string)'
    >>> strip_balanced_edge_parens('(This is a super (string')
    '(This is a super (string'
    >>> strip_balanced_edge_parens('(This is a super (string)')
    '(This is a super (string)'
    """
    if s.startswith('(') and s.endswith(')'):
        c = s[1:-1]
        if '(' not in c and ')' not in c:
            return c
    return s

################################################################################
# CANDIDATE LINES SELECTION
################################################################################


remove_non_chars = re.compile(r'[^a-z0-9]').sub


def prep_line(line):
    """
    Return a tuple of (line, line with only chars) from a line of text prepared
    for candidate and other checks or None.
    """
    line = prepare_text_line(line.lower(), dedeb=False)
    chars_only = remove_non_chars('', line)
    return line, chars_only.strip()


is_only_digit_and_punct = re.compile('^[^A-Za-z]+$').match


def is_candidate(prepared_line):
    """
    Return True if a prepared line is a candidate line for copyright detection
    """
    if not prepared_line:
        return False

    if is_only_digit_and_punct(prepared_line):
        if TRACE:
            logger_debug(
                f'is_candidate: is_only_digit_and_punct:\n{prepared_line!r}')

        return False

    if copyrights_hint.years(prepared_line):
        return True
    else:
        pass

    for marker in copyrights_hint.statement_markers:
        if marker in prepared_line:
            return True


def is_inside_statement(
    chars_only_line,
    markers=('copyright', 'copyrights', 'copyrightby',) + copyrights_hint.all_years,
):
    """
    Return True if a line ends with some strings that indicate we are still
    inside a statement.
    """
    return chars_only_line and chars_only_line.endswith(markers)


def is_end_of_statement(chars_only_line):
    """
    Return True if a line ends with some strings that indicate we are at the end
    of a statement.
    """
    return (
        chars_only_line
        and chars_only_line.endswith(('rightreserved', 'rightsreserved'))
    )


has_trailing_year = re.compile(r'(?:19\d\d|20[0-4]\d)+$').findall


def candidate_lines(numbered_lines):
    """
    Yield groups of candidate line lists where each list element is a tuple of
    (line number,  line text) given an iterable of ``numbered_lines`` as tuples
    of (line number,  line text) .

    A candidate line is a line of text that may contain copyright statements.
    A few lines before and after a candidate line are also included.
    """
    candidates = deque()
    candidates_append = candidates.append
    candidates_clear = candidates.clear

    # used as a state and line counter
    in_copyright = 0

    # the previous line (chars only)
    previous_chars = None
    for numbered_line in numbered_lines:
        if TRACE:
            logger_debug(
                f'# candidate_lines: evaluating line: {numbered_line!r}')

        _line_number, line = numbered_line

        # FIXME: we should get the prepared text from here and return
        # effectively pre-preped lines... but the prep taking place here is
        # different?
        prepped, chars_only = prep_line(line)

        if is_end_of_statement(chars_only):
            candidates_append(numbered_line)

            if TRACE:
                cands = list(candidates)
                logger_debug(
                    '   candidate_lines: is EOS: yielding candidates\n'
                    f'    {cands}r\n\n'
                )

            yield list(candidates)
            candidates_clear()
            in_copyright = 0
            previous_chars = None

        elif is_candidate(prepped):
            # the state is now "in copyright"
            in_copyright = 2
            candidates_append(numbered_line)

            previous_chars = chars_only
            if TRACE: logger_debug('   candidate_lines: line is candidate')

        elif 's>' in line:
            # this is for debian-style <s></s> copyright name tags
            # the state is now "in copyright"
            in_copyright = 2
            candidates_append(numbered_line)

            previous_chars = chars_only
            if TRACE:
                logger_debug('   candidate_lines: line is <s></s>candidate')

        elif in_copyright > 0:
            # these are a sign that the copyrights continue after
            # a possibly empty line
            # see https://github.com/nexB/scancode-toolkit/issues/1565
            # if these are no present we treat empty lines... as empty!
            if (
                (not chars_only)
                and (
                    not previous_chars.endswith((
                        'copyright',
                        'copyrights',
                        'and',
                        'by',
                    ))
                )
                and not has_trailing_year(previous_chars)
            ):

                # completely empty or only made of punctuations
                if TRACE:
                    cands = list(candidates)
                    logger_debug(
                        '   candidate_lines: empty: yielding candidates\n'
                        f'    {cands}r\n\n'
                    )

                yield list(candidates)
                candidates_clear()
                in_copyright = 0
                previous_chars = None

            else:
                candidates_append(numbered_line)
                # and decrement our state
                in_copyright -= 1
                if TRACE:
                    logger_debug('   candidate_lines: line is in copyright')

        elif candidates:
            if TRACE:
                cands = list(candidates)
                logger_debug(
                    '    candidate_lines: not in COP: yielding candidates\n'
                    f'    {cands}r\n\n'
                )

            yield list(candidates)
            candidates_clear()
            in_copyright = 0
            previous_chars = None

    # finally
    if candidates:
        if TRACE:
            cands = list(candidates)
            logger_debug(
                'candidate_lines: finally yielding candidates\n'
                f'    {cands}r\n\n'
            )

        yield list(candidates)

################################################################################
# TEXT PRE PROCESSING
################################################################################


# this catches tags but not does not remove the text inside tags
remove_tags = re.compile(
    r'<'
     r'[(-\-)\?\!\%\/]?'
     r'[a-gi-vx-zA-GI-VX-Z][a-zA-Z#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]*'
     r'[a-zA-Z0-9#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]+'
    r'\/?>',
    re.MULTILINE | re.UNICODE
).sub


def strip_markup(text, dedeb=True):
    """
    Strip markup tags from ``text``.

    If ``dedeb`` is True, remove "Debian" <s> </s> markup tags seen in
    older copyright files.
    """
    text = remove_tags(' ', text)
    # Debian copyright file markup
    if dedeb:
        return text.replace('</s>', '').replace('<s>', '').replace('<s/>', '')
    else:
        return text


# this catches the common C-style percent string formatting codes
remove_printf_format_codes = re.compile(r' [\#\%][a-zA-Z] ').sub

remove_punctuation = re.compile(r'[\*#"%\[\]\{\}`]+').sub

remove_ascii_decorations = re.compile(r'[-_=!\\*]{2,}|/{3,}').sub

fold_consecutive_quotes = re.compile(r"\'{2,}").sub

# less common rem comment line prefix in dos
# less common dnl comment line prefix in autotools am/in
remove_comment_markers = re.compile(r'^(rem|\@rem|dnl)\s+').sub

# common comment line prefix in man pages
remove_man_comment_markers = re.compile(r'.\\"').sub


def prepare_text_line(line, dedeb=True, to_ascii=True):
    """
    Prepare a text ``line`` for copyright detection.

    If ``dedeb`` is True, remove "Debian" <s> </s> markup tags seen in
    older copyright files.

    If ``to_ascii`` convert the text to ASCII characters.
    """
    # remove some junk in man pages: \(co
    line = (line
        .replace('\\\\ co', ' ')
        .replace('\\ co', ' ')
        .replace('(co ', ' ')
    )
    line = remove_printf_format_codes(' ', line)

    # less common comment line prefixes
    line = remove_comment_markers(' ', line)
    line = remove_man_comment_markers(' ', line)

    line = (line
        # C and C++ style comment markers
        .replace('/*', ' ').replace('*/', ' ')
        .strip().strip('/*#')
        # un common pipe chars in some ascii art
        .replace('|', ' ')

        # normalize copyright signs and spacing around them
        .replace('"Copyright', '" Copyright')
        .replace('( C)', ' (c) ')
        .replace('(C)', ' (c) ')
        .replace('(c)', ' (c) ')
        # the case of \251 is tested by 'weirdencoding.h'
        .replace('©', ' (c) ')
        .replace('\251', ' (c) ')
        .replace('&copy;', ' (c) ')
        .replace('&copy', ' (c) ')
        .replace('&#169;', ' (c) ')
        .replace('&#xa9;', ' (c) ')
        .replace('&#XA9;', ' (c) ')
        .replace('u00A9', ' (c) ')
        .replace('u00a9', ' (c) ')
        .replace('\xa9', ' (c) ')
        .replace('\\XA9', ' (c) ')
        # \xc2 is a Â
        .replace('\xc2', '')
        .replace('\\xc2', '')

        # not really a dash: an emdash
        .replace('–', '-')

        # TODO: add more HTML entities replacements
        # see http://www.htmlhelp.com/reference/html40/entities/special.html
        # convert html entities &#13;&#10; CR LF to space
        .replace('&#13;&#10;', ' ')
        .replace('&#13;', ' ')
        .replace('&#10;', ' ')

        # spaces
        .replace('&ensp;', ' ')
        .replace('&emsp;', ' ')
        .replace('&thinsp;', ' ')

        # common named HTML entities
        .replace('&quot;', '"')
        .replace('&#34;', '"')
        .replace('&amp;', '&')
        .replace('&#38;', '&')
        .replace('&gt;', '>')
        .replace('&#62;', '>')
        .replace('&lt;', '<')
        .replace('&#60;', '<')

        # normalize (possibly repeated) quotes to unique single quote '
        # backticks ` and "
        .replace('`', u"'")
        .replace('"', u"'")
    )
    # keep only one quote
    line = fold_consecutive_quotes(u"'", line)

    # treat some escaped literal CR, LF, tabs, \00 as new lines
    # such as in code literals: a="\\n some text"
    line = (line
        .replace('\\t', ' ')
        .replace('\\n', ' ')
        .replace('\\r', ' ')
        .replace('\\0', ' ')

        # TODO: why backslashes?
        .replace('\\', ' ')

        # replace ('
        .replace('("', ' ')
        # some trailing garbage ')
        .replace(u"')", ' ')
        .replace(u"],", ' ')
    )
    # note that we do not replace the debian tag by a space:  we remove it
    line = strip_markup(line, dedeb=dedeb)

    line = remove_punctuation(' ', line)

    # normalize spaces around commas
    line = line.replace(' , ', ', ')

    # remove ASCII "line decorations"
    # such as in --- or === or !!! or *****
    line = remove_ascii_decorations(' ', line)

    # in apache'>Copyright replace ">" by "> "
    line = line.replace('>', '> ').replace('<', ' <')

    # normalize to ascii text
    if to_ascii:
        line = toascii(line, translit=True)

    # normalize to use only LF as line endings so we can split correctly
    # and keep line endings
    line = unixlinesep(line)

    # strip verbatim back slash and comment signs again at both ends of a line
    # FIXME: this is done at the start of this function already
    line = line.strip('\\/*#%;')

    # normalize spaces
    line = ' '.join(line.split())

    return line
