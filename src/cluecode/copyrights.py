#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import, print_function

from collections import deque
import logging
import os
import re

import nltk
nltk3 = nltk.__version__.startswith('3')

import commoncode
from textcode import analysis
from cluecode import copyrights_hint


logger = logging.getLogger(__name__)
if os.environ.get('SC_COPYRIGHT_DEBUG'):
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


"""
Detect and collect copyright statements.

The process consists in:
 - prepare and cleanup text
 - identify regions of text that may contain copyright (using hints)
 - tag the text for parts-of-speech (POS) to identify various copyright
   statements parts such as dates, names ("named entities"), etc. This is done
   using NLTK POS tagging
 - feed the tagged text to a parsing grammar describing actual copyright
   statements
 - yield copyright statements, years, holder and authors with start and end line
   from the parse tree, eventually performing some minor cleanups.
"""


def detect_copyrights(location):
    """
    Yield tuples of:
    (copyrights list, authors list, years list, holders list, start line, end line)
    detected in file at location.
    """
    detector = CopyrightDetector()
    for numbered_lines in candidate_lines(analysis.text_lines(location)):
        detected = detector.detect(numbered_lines)
        cp, auth, yr, hold, _start, _end = detected
        if any([cp, auth, yr, hold]):
            yield detected


def detect(location):
    """
    Return lists of detected copyrights, authors, years and holders
    in file at location.
    Deprecated legacy entry point.
    """
    copyrights = []
    authors = []
    years = []
    holders = []
    for cp, auth, yr, hold, _start, _end in detect_copyrights(location):
        copyrights.extend(cp)
        authors.extend(auth)
        years.extend(yr)
        holders.extend(hold)
    return copyrights, authors, years, holders


# FIXME: multi-tokens patterns are likely not behaving as expected
# FIXME: patterns could be greatly simplified
patterns = [
    # TODO: this needs to be simplified:
    # TODO: in NLTK 3.0 this will fail because of this bug:
    # https://github.com/nltk/nltk/issues/1025

    # JUNK are things to ignore
    # All Rights Reserved. should be a terminator/delimiter.
    (r'^([Aa]ll [Rr]ights? [Rr]eserved|ALL RIGHTS? RESERVED|[Aa]ll|ALL)$', 'JUNK'),
    (r'^([Rr]eserved|RESERVED)[,]?$', 'JUNK'),

    # found in crypto certificates and LDAP
    (r'^(O=|OU=|OU|XML)$', 'JUNK'),
    (r'^(Parser|Dual|Crypto|NO|PART|[Oo]riginall?y?|[Rr]epresentations?\.?)$', 'JUNK'),
    (r'^(Refer|Apt|Agreement|Usage|Please|Based|Upstream|Files?|Filename:?|Description:?|Holder?s|HOLDER?S|[Pp]rocedures?|You|Everyone)$', 'JUNK'),
    (r'^(Rights?|Unless|rant|Subject|Acknowledgements?|Special)$', 'JUNK'),
    (r'^(Derivative|Work|[Ll]icensable|[Ss]ince|[Ll]icen[cs]e[\.d]?|[Ll]icen[cs]ors?|under|COPYING)$', 'JUNK'),
    (r'^(TCK|Use|[Rr]estrictions?|[Ii]ntroduction)$', 'JUNK'),
    (r'^([Ii]ncludes?|[Vv]oluntary|[Cc]ontributions?|[Mm]odifications?)$', 'JUNK'),
    (r'^(CONTRIBUTORS?|OTHERS?|Contributors?\:)$', 'JUNK'),
    (r'^(Company:|For|File|Last|[Rr]elease|[Cc]opyrighting)$', 'JUNK'),
    (r'^Authori.*$', 'JUNK'),
    (r'^[Bb]uild$', 'JUNK'),
    #
    (r'^Copyleft|LegalCopyright|AssemblyCopyright|Distributed$', 'JUNK'),


    # Bare C char is COPYRIGHT SIGN
    # (r'^C$', 'COPY'),

    # exceptions to composed proper nouns, mostly debian copyright-related
    # FIXME: may be lowercase instead?
    (r'^(Title:?|Debianized-By:?|Upstream-Maintainer:?|Content-MD5)$', 'JUNK'),
    (r'^(Upstream-Author:?|Packaged-By:?)$', 'JUNK'),

    # NOT a copyright symbol (ie. "copyrighted."): treat as NN
    (r'^[Cc](opyright(s|ed)?|OPYRIGHT(S|ED))\.$', 'NN'),
    # copyright word or symbol
    # note the leading @ .... this may be a source of problems
    (r'.?(@?([Cc]opyright)s?:?|[(][Cc][)]|(COPYRIGHT)S?:?)', 'COPY'),

    # copyright in markup, until we strip markup: apache'>Copyright
    (r'[A-Za-z0-9]+[\'">]+[Cc]opyright', 'COPY'),

    # company suffix
    (r'^([Ii]nc[.]?|[I]ncorporated|[Cc]ompany|Limited|LIMITED).?$', 'COMP'),
    # company suffix
    (r'^(INC(ORPORATED|[.])?|CORP(ORATION|[.])?|FOUNDATION|GROUP|COMPANY|[(]tm[)]).?$|[Ff]orum.?', 'COMP'),
    # company suffix
    (r'^([cC]orp(oration|[.])?|[fF]oundation|[Aa]lliance|Working|[Gg]roup|[Tt]echnolog(y|ies)|[Cc]ommunit(y|ies)|[Mm]icrosystems.?|[Pp]roject|[Tt]eams?|[Tt]ech).?$', 'COMP'),
    # company suffix : LLC, LTD, LLP followed by one extra char
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.,$', 'COMP'),
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.?,?$', 'COMP'),
    (r'^([Ll][Ll][CcPp]|[Ll][Tt][Dd])\.$', 'COMP'),
    # company suffix : SA, SAS, AG, AB, AS, CO, labs followed by a dot
    (r'^(S\.?A\.?S?|Sas|sas|A[GBS]|Labs?|[Cc][Oo]\.|Research|INRIA).?$', 'COMP'),
    # (german) company suffix
    (r'^[Gg][Mm][Bb][Hh].?$', 'COMP'),
    # university
    (r'^[Uu]niv([.]|ersit(y|e|at?|ad?))$', 'UNI'),
    # institutes
    (r'^[Ii]nstitut(s|o|os|e|es|et|a|at|as|u|i)?$', 'NNP'),
    # "holders" is considered as a common noun
    (r'^([Hh]olders?|HOLDERS?|[Rr]espective)$', 'NN'),

    # (r'^[Cc]ontributors?\.?', 'NN'),
    # "authors" or "contributors" is interesting, and so a tag of its own
    (r'^[Aa]uthors?$', 'AUTH'),
    (r'^[Aa]uthor\(s\)$', 'AUTH'),
    (r'^[Cc]ontribut(ors?|ing)\.?$', 'AUTH'),

    # commiters is interesting, and so a tag of its own
    (r'[Cc]ommitters?', 'COMMIT'),
    # same for maintainer, developed, etc...
    (r'^(([Rr]e)?[Cc]oded|[Mm]odified|[Mm]ai?nt[ea]ine(d|r)|[Ww]ritten|[Dd]eveloped)$', 'AUTH2'),
    # author
    (r'@author', 'AUTH'),
    # of
    (r'^[Oo][Ff]|[Dd][Ee]$', 'OF'),
    # in
    (r'^in$', 'IN'),
    # by
    (r'^by$', 'BY'),
    # conjunction: and
    (r'^([Aa]nd|&)$', 'CC'),
    # conjunction: or. Even though or is not conjunctive ....
    # (r'^or$', 'CC'),
    # conjunction: or. Even though or is not conjunctive ....
    # (r'^,$', 'CC'),
    # ie. in things like "Copyright (c) 2012 John Li and others"
    (r'^others$', 'OTH'),
    # in year ranges: dash, or 'to': "1990-1995", "1990/1995" or "1990 to 1995"
    (r'^([-/]|to)$', 'DASH'),

    # explicitly ignoring these words: FIXME: WHY?
    (r'^([Tt]his|THIS|[Pp]ermissions?|PERMISSIONS?|All)$', 'NN'),

    # in dutch/german names, like Marco van Basten, or Klemens von Metternich
    # and Spanish/French Da Siva and De Gaulle
    (r'^(([Vv][ao]n)|[Dd][aeu])$', 'VAN'),

    # year
    (r'^[(]?(19|20)[0-9]{2}((\s)*([,-]|to)(\s)*(19|20)?[0-9]{2})*[)]?', 'YR'),
    # cardinal numbers
    (r'^-?[0-9]+(.[0-9]+)?.?$', 'CD'),

    # exceptions to proper nouns
    (r'^(The|Commons|AUTHOR|software)$', 'NN'),

    # composed proper nouns, ie. Jean-Claude or ST-Microelectronics
    # FIXME: what about a variant with spaces around the dash?
    (r'^[A-Z][a-zA-Z]*[-][A-Z]?[a-zA-Z]+.?$', 'NNP'),

    # proper nouns with digits
    (r'^[A-Z][a-z0-9]+.?$', 'NNP'),
    # saxon genitive, ie. Philippe's
    (r"^[A-Z][a-z]+[']s$", 'NNP'),
    # dotted name, ie. P.
    (r"^([A-Z][.]?|[A-Z]+[\.])$", 'PN'),
    # proper noun with some separator and trailing comma
    (r"^[A-Z]+[.][A-Z][a-z]+[,]?$", 'NNP'),

    # proper noun with apostrophe ': D'Orleans, D'Arcy, T'so, Ts'o
    (r"^[A-Z][[a-z]?['][A-Z]?[a-z]+[,.]?$", 'NNP'),

    # proper noun with apostrophe ': d'Itri
    (r"^[a-z]['][A-Z]?[a-z]+[,\.]?$", 'NNP'),

    # all CAPS word, at least 1 char long such as MIT, including an optional trailing comma or dot
    (r'^[A-Z0-9]+[,]?$', 'CAPS'),
    # all caps word 3 chars and more, enclosed in parens
    (r'^\([A-Z0-9]{2,}\)$', 'CAPS'),

    # proper noun:first CAP, including optional trailing comma
    (r'^[A-Z][a-zA-Z0-9]+[,]?$', 'NNP'),

    # email
    (r'[a-zA-Z0-9\+_\-\.\%]+@[a-zA-Z0-9][a-zA-Z0-9\+_\-\.\%]*\.[a-zA-Z]{2,5}?', 'EMAIL'),

    # email eventually in parens or brackets. The closing > or ) is optional
    (r'[\<\(][a-zA-Z0-9\+_\-\.\%]+@[a-zA-Z0-9][a-zA-Z0-9\+_\-\.\%]*\.[a-zA-Z]{2,5}?[\>\)]?', 'EMAIL'),

    # URLS such as ibm.com
    # TODO: add more extensions?
    (r'<?a?.(href)?.[a-z0-9A-Z\-\.\_]+\.(com|net|info|org|us|io|edu|co\.[a-z][a-z]|eu|biz)', 'URL'),
    # derived from regex in cluecode.finder
    (r'<?a?.(href)?.('
     r'(?:http|ftp|sftp)s?://[^\s<>\[\]"]+'
     r'|(?:www|ftp)\.[^\s<>\[\]"]+'
     r')', 'URL'),

    # AT&T (the company), needed special handling
    (r'^AT&T$', 'ATT'),
    # comma as a conjunction
    (r'^,$', 'CC'),
    # .\ is not a noun
    (r'^\.\\$', 'JUNK'),

    # nouns (default)
    (r'.+', 'NN'),
]

# Comments in the Grammar are lines that start with #
grammar = """
    COPY: {<COPY>}
    YR-RANGE: {<YR>+ <CC> <YR>}
    YR-RANGE: {<YR> <DASH>* <YR|CD>+}
    YR-RANGE: {<CD>? <YR>+}
    YR-RANGE: {<YR>+ }

    NAME: {<NNP> <VAN|OF> <NN*> <NNP>}
    NAME: {<NNP> <PN> <VAN> <NNP>}

# the Regents of the University of California
    COMPANY: {<BY>? <NN> <NNP> <OF> <NN> <UNI> <OF> <COMPANY|NAME|NAME2|NAME3><COMP>?}


# "And" some name
    ANDCO: {<CC>+ <NN> <NNP>+<UNI|COMP>?}
    ANDCO: {<CC>+ <NNP> <NNP>+<UNI|COMP>?}
    ANDCO: {<CC>+ <COMPANY|NAME|NAME2|NAME3>+<UNI|COMP>?}
    COMPANY: {<COMPANY|NAME|NAME2|NAME3> <ANDCO>+}


# rare "Software in the public interest, Inc."
    COMPANY: {<COMP> <CD> <COMP>}
    COMPANY: {<NNP> <IN><NN> <NNP> <NNP>+<COMP>?}

    COMPANY: {<NNP> <CC> <NNP> <COMP>}
    COMPANY: {<NNP|CAPS> <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <NNP|CAPS>? <COMP> <COMP>?}
    COMPANY: {<UNI|NNP> <VAN|OF> <NNP>+ <UNI>?}
    COMPANY: {<NNP>+ <UNI>}
    COMPANY: {<COMPANY> <CC> <COMPANY>}
    COMPANY: {<ATT> <COMP>?}
    COMPANY: {<COMPANY> <CC> <NNP>}
    # Group 42, Inc

# Typical names
    NAME: {<NNP|PN>+ <NNP>+}
    NAME: {<NNP> <PN>? <NNP>+}
    NAME: {<NNP> <NNP>}
    NAME: {<NNP> <NN> <EMAIL>}
    NAME: {<NNP> <PN|VAN>? <PN|VAN>? <NNP>}
    NAME: {<NNP> <NN> <NNP>}
    NAME: {<NNP> <COMMIT>}
    NAME: {<NN> <NNP> <ANDCO>}
    NAME: {<NN>? <NNP> <CC> <NAME>}
    NAME: {<NN>? <NNP> <OF> <NN>? <NNP> <NNP>?}
    NAME: {<NAME> <CC> <NAME>}
    COMPANY: {<NNP> <IN> <NN>? <COMPANY>}

    NAME2: {<NAME> <EMAIL>}
    NAME3: {<YR-RANGE> <NAME2|COMPANY>+}
    NAME: {<NAME|NAME2>+ <OF> <NNP> <OF> <NN>? <COMPANY>}
    NAME: {<NAME|NAME2>+ <CC|OF>? <NAME|NAME2|COMPANY>}
    NAME3: {<YR-RANGE> <NAME>+}
    NAME: {<NNP> <OF> <NNP>}
    NAME: {<NAME> <NNP>}
    NAME: {<NN|NNP|CAPS>+ <CC> <OTH>}
    NAME: {<NNP> <CAPS>}
    NAME: {<CAPS> <DASH>? <NNP|NAME>}
    NAME: {<NNP> <CD> <NNP>}
    NAME: {<COMP> <NAME>+}

    NAME: {<NNP|CAPS>+ <AUTH>}


# Companies
    COMPANY: {<NAME|NAME2|NAME3|NNP>+ <OF> <NN>? <COMPANY|COMP>}
    COMPANY: {<NNP> <COMP> <COMP>}
    COMPANY: {<NN>? <COMPANY|NAME|NAME2> <CC> <COMPANY|NAME|NAME2>}
    COMPANY: {<COMP|NNP> <NN> <COMPANY> <NNP>+}
    COMPANY: {<COMPANY> <CC> <AUTH>}
    COMPANY: {<NN> <COMP>+}
    COMPANY: {<URL>}

# Trailing Authors
    COMPANY: {<NAME|NAME2|NAME3|NNP>+ <AUTH>}

# "And" some name
    ANDCO: {<CC> <NNP> <NNP>+}
    ANDCO: {<CC> <COMPANY|NAME|NAME2|NAME3>+}
    COMPANY: {<COMPANY|NAME|NAME2|NAME3> <ANDCO>+}
    NAME: {<NNP> <ANDCO>+}

    NAME: {<BY> <NN> <AUTH>}

# Various forms of copyright statements
    COPYRIGHT: {<COPY> <NAME> <COPY> <YR-RANGE>}

    COPYRIGHT: {<COPY> <COPY> <BY>? <COMPANY|NAME*|YR-RANGE>* <BY>? <EMAIL>+}
    COPYRIGHT: {<COPY> <BY>? <COMPANY|NAME*|YR-RANGE>* <BY>? <EMAIL>+}

    COPYRIGHT: {<COPY> <COPY> <NAME|NAME2|NAME3> <CAPS> <YR-RANGE>}
    COPYRIGHT: {<COPY> <NAME|NAME2|NAME3> <CAPS> <YR-RANGE>}

    COPYRIGHT: {<COPY> <COPY> <NAME|NAME2|NAME3>+ <YR-RANGE>*}
    COPYRIGHT: {<COPY> <NAME|NAME2|NAME3>+ <YR-RANGE>*}

    COPYRIGHT: {<COPY> <COPY> <CAPS|NNP>+ <CC> <NN> <COPY> <YR-RANGE>?}
    COPYRIGHT: {<COPY> <CAPS|NNP>+ <CC> <NN> <COPY> <YR-RANGE>?}

    COPYRIGHT: {<COPY> <COPY> <BY>? <COMPANY|NAME*>+ <YR-RANGE>*}
    COPYRIGHT: {<COPY> <BY>? <COMPANY|NAME*>+ <YR-RANGE>*}

    COPYRIGHT: {<NNP>? <COPY> <COPY> (<YR-RANGE>+ <BY>? <NN>? <COMPANY|NAME|NAME2>+ <EMAIL>?)+}
    COPYRIGHT: {<NNP>? <COPY> (<YR-RANGE>+ <BY>? <NN>? <COMPANY|NAME|NAME2>+ <EMAIL>?)+}

    COPYRIGHT: {<COPY> <COPY> <NN> <NAME> <YR-RANGE>}
    COPYRIGHT: {<COPY> <NN> <NAME> <YR-RANGE>}

    COPYRIGHT: {<COPY> <COPY> <COMP>+}

    COPYRIGHT: {<COPY> <COPY> <NN>+ <COMPANY|NAME|NAME2>+}

    COPYRIGHT: {<COPY> <COPY> <NN> <NN>? <COMP> <YR-RANGE>?}
    COPYRIGHT: {<COPY> <NN> <NN>? <COMP> <YR-RANGE>?}

    COPYRIGHT: {<COPY> <COPY> <NN> <NN>? <COMP> <YR-RANGE>?}
    COPYRIGHT: {<COPY> <NN> <NN>? <COMPANY> <YR-RANGE>?}

    COPYRIGHT: {<COPY> <COPY> <YR-RANGE|NNP> <CAPS|BY>? <NNP|YR-RANGE|NAME>+}
    COPYRIGHT: {<COPY> <YR-RANGE|NNP> <CAPS|BY>? <NNP|YR-RANGE|NAME>+}

    COPYRIGHT: {<COPY> <COPY> <NNP>+}

    # Copyright (c) 1995, 1996 The President and Fellows of Harvard University
    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NN> <NNP> <ANDCO>}

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NN> <AUTH>}

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <BY> <NN> <NN> <NAME>}
    COPYRIGHT2: {<COPY> <YR-RANGE> <BY> <NN> <NN> <NAME>}

    COPYRIGHT2: {<COPY> <COPY><NN>? <COPY> <YR-RANGE> <BY> <NN>}
    COPYRIGHT2: {<COPY> <NN>? <COPY> <YR-RANGE> <BY> <NN>}

    COPYRIGHT2: {<COPY> <COPY><NN> <YR-RANGE> <BY> <NAME>}
    COPYRIGHT2: {<COPY> <NN> <YR-RANGE> <BY> <NAME>}

    COPYRIGHT2: {<COPY> <COPY><YR-RANGE> <DASH> <NAME2|NAME>}
    COPYRIGHT2: {<COPY> <YR-RANGE> <DASH> <NAME2|NAME>}

    COPYRIGHT2: {<COPY> <COPY> <YR-RANGE> <NNP> <NAME>}
    COPYRIGHT2: {<COPY> <YR-RANGE> <NNP> <NAME>}

    COPYRIGHT2: {<NAME> <COPY> <YR-RANGE>}

    COPYRIGHT2: {<COPY> <COPY> <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>*}
    COPYRIGHT2: {<COPY> <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>*}

    COPYRIGHT2: {<COPY> <COPY> <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <COMPANY>}
    COPYRIGHT2: {<COPY> <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <COMPANY>}

    COPYRIGHT2: {<COPY> <COPY> <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <DASH> <COMPANY>}
    COPYRIGHT2: {<COPY> <NN|CAPS>? <YR-RANGE>+ <NN|CAPS>* <DASH> <COMPANY>}

    COPYRIGHT2: {<NNP|NAME|COMPANY> <COPYRIGHT2>}

    COPYRIGHT: {<COPYRIGHT> <NN> <COMPANY>}

    COPYRIGHT: {<COPY> <COPY> <BY>? <NN> <COMPANY>}
    COPYRIGHT: {<COPY> <BY>? <NN> <COMPANY>}

    COPYRIGHT: {<COMPANY> <NN> <NAME> <COPYRIGHT2>}
    COPYRIGHT: {<COPYRIGHT2> <COMP> <COMPANY>}
    COPYRIGHT: {<COMPANY> <NN> <COPYRIGHT2>}
    COPYRIGHT: {<COPYRIGHT2> <NNP> <CC> <COMPANY>}


# copyrights in the style of Scilab/INRIA
    COPYRIGHT: {<NNP> <NN> <COPY> <NNP>}
    COPYRIGHT: {<NNP> <COPY> <NNP>}

# Authors
    AUTH: {<AUTH2>+ <BY>}
    AUTHOR: {<AUTH>+ <NN>? <COMPANY|NAME|YR-RANGE>* <BY>? <EMAIL>+}
    AUTHOR: {<AUTH>+ <NN>? <COMPANY|NAME|NAME2>+ <YR-RANGE>*}
    AUTHOR: {<AUTH>+ <YR-RANGE>+ <BY>? <COMPANY|NAME|NAME2>+}
    AUTHOR: {<AUTH>+ <YR-RANGE|NNP> <NNP|YR-RANGE>+}
    AUTHOR: {<AUTH>+ <NN|CAPS>? <YR-RANGE>+}
    AUTHOR: {<COMPANY|NAME|NAME2>+ <AUTH>+ <YR-RANGE>+}
    AUTHOR: {<YR-RANGE> <NAME|NAME2>+}
    AUTHOR: {<NAME2>+}
    AUTHOR: {<AUTHOR> <CC> <NN>? <AUTH>}
    AUTHOR: {<BY> <EMAIL>}
    ANDAUTH: {<CC> <AUTH|NAME>+}
    AUTHOR: {<AUTHOR> <ANDAUTH>+}

# Compounded statements usings authors
    # found in some rare cases with a long list of authors.
    COPYRIGHT: {<COPY> <BY> <AUTHOR>+ <YR-RANGE>*}

    COPYRIGHT: {<AUTHOR> <COPYRIGHT2>}
    COPYRIGHT: {<AUTHOR> <YR-RANGE>}
"""


def strip_numbers(s):
    """
    Return a string removing words made only of numbers. If there is an
    exception or s is not a string, return s as-is.
    """
    if s:
        s = u' '.join([x for x in s.split(' ') if not x.isdigit()])
    return s


def strip_some_punct(s):
    """
    Return a string stripped from some leading and trailing punctuations.
    """
    if s:
        s = s.strip(''','"};''')
        s = s.lstrip(')')
        s = s.rstrip('&(-_')
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
    `paren` is a pair of characters to balance  such as (), <>, [] , {}.

    For instance:
    >>> strip_unbalanced_parens('This is a super string', '()')
    'This is a super string'

    >>> strip_unbalanced_parens('This is a super(c) string', '()')
    'This is a super(c) string'

    >>> strip_unbalanced_parens('This ((is a super(c) string))', '()')
    'This ((is a super(c) string))'

    >>> strip_unbalanced_parens('This )(is a super(c) string)(', '()')
    'This  (is a super(c) string) '

    >>> strip_unbalanced_parens(u'This )(is a super(c) string)(', '()')
    u'This  (is a super(c) string) '

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
    stack = []
    for i, c in enumerate(s):
        if c == start:
            stack.append((i, c,))
        elif c == end:
            try:
                stack.pop()
            except IndexError:
                unbalanced.append((i, c,))

    unbalanced.extend(stack)
    pos_to_del = set([i for i, c in unbalanced])
    cleaned = [c if i not in pos_to_del else ' ' for i, c in enumerate(s)]
    return type(s)('').join(cleaned)


def refine_copyright(c):
    """
    Refine a detected copyright string.
    FIXME: the grammar should not allow this to happen.
    """
    c = strip_some_punct(c)
    c = fix_trailing_space_dot(c)
    c = strip_unbalanced_parens(c, '()')
    c = strip_unbalanced_parens(c, '<>')
    c = strip_unbalanced_parens(c, '[]')
    c = strip_unbalanced_parens(c, '{}')
    # FIXME: this should be in the grammar, but is hard to get there right
    # these are often artifacts of markup
    c = c.replace('Copyright Copyright', 'Copyright')
    c = c.replace('Copyright copyright', 'Copyright')
    c = c.replace('copyright copyright', 'Copyright')
    c = c.replace('copyright Copyright', 'Copyright')
    c = c.replace('copyright\'Copyright', 'Copyright')
    c = c.replace('copyright"Copyright', 'Copyright')
    c = c.replace('copyright\' Copyright', 'Copyright')
    c = c.replace('copyright" Copyright', 'Copyright')
    s = c.split()

    # fix traliing garbage, captured by the grammar
    if s[-1] in ('Parts', 'Any',):
        s = s[:-1]
    # this is hard to catch otherwise, unless we split the author
    # vs copyright grammar in two. Note that AUTHOR and Authors should be kept
    if s[-1] == 'Author':
        s = s[:-1]

    s = u' '.join(s)
    return s.strip()


def refine_author(c):
    """
    Refine a detected author
    FIXME: the grammar should not allow this to happen.
    """
    c = strip_some_punct(c)
    c = strip_numbers(c)
    c = strip_unbalanced_parens(c, '()')
    c = strip_unbalanced_parens(c, '<>')
    c = strip_unbalanced_parens(c, '[]')
    c = strip_unbalanced_parens(c, '{}')
    c = c.split()
    # this is hard to catch otherwise, unless we split the author vs copyright grammar in two
    if c[0].lower() == 'author':
        c = c[1:]
    c = u' '.join(c)
    return c.strip()


def refine_date(c):
    """
    Refine a detected date or date range.
    FIXME: the grammar should not allow this to happen.
    """
    c = strip_some_punct(c)
    return c


def is_junk(c):
    """
    Return True if string `c` is a junk copyright that cannot be resolved
    otherwise by the parsing.
    It would be best not to have to resort to this, but this is practical.
    """
    junk = set([
        'copyrighted by their authors',
        'copyrighted by their authors.',
        'copyright holder or other authorized',
        'copyright holder who authorizes',
        'copyright holder has authorized',
        'copyright holder nor the author',
        'copyright holder(s) or the author(s)',

        'copyright owner or entity authorized',
        'copyright owner or contributors',

        'copyright for a new language file should be exclusivly the authors',

        'copyright holder or said author',
        'copyright holder, or any author',
        'copyrighted material, only this license, or another one contracted with the authors',
        'copyright notices, authorship',
        'copyright holder means the original author(s)',
        "copyright notice. timevar.def's author",

        "copyright holder or simply that it is author-maintained'.",
        "copyright holder or simply that is author-maintained'.",
        '(c) if you bring a patent claim against any contributor',
        'copyright-check writable-files m4-check author_mark_check',
        # 'copyrighting it yourself or claiming authorship'
    ])
    return c.lower() in junk


class CopyrightDetector(object):
    """
    Class to detect copyrights and authorship.
    """
    def __init__(self):
        self.tagger = nltk.RegexpTagger(patterns)
        self.chunker = nltk.RegexpParser(grammar)

    @staticmethod
    def as_str(node):
        """
        Return a parse tree node as a space-normalized string.
        """
        node_string = ' '.join(k for k, _ in node.leaves())
        return u' '.join(node_string.split())

    def detect(self, numbered_lines):
        """
        Return a sequence of tuples (copyrights, authors, years, holders)
        detected in a sequence of numbered line tuples.
        """
        numbered_lines = list(numbered_lines)
        numbers = [n for n, _l in numbered_lines]
        start_line = min(numbers)
        end_line = max(numbers)
        logger.debug('CopyrightDetector:detect:lines numbers: %(start_line)d->%(end_line)d' % locals())
        tokens = self.get_tokens(numbered_lines)

        # we accumulate detected items in these synchronized lists
        # this could be a single list of namedtuples
        # or a list of dicts instead
        copyrights, authors, years, holders = [], [], [], []

        if not tokens:
            return copyrights, authors, years, holders, None, None

        # first, POS tag each token using token regexes
        tagged_text = self.tagger.tag(tokens)
        logger.debug('CopyrightDetector:tagged_text: ' + str(tagged_text))

        # then build a parse tree based on tagged tokens
        tree = self.chunker.parse(tagged_text)
        logger.debug('CopyrightDetector:parse tree: ' + str(tree))

        def collect_year_and_holder(detected_copyright):
            """
            Walk the a parse sub-tree starting with the `detected_copyright`
            node collecting all years and holders.
            """
            for copyr in detected_copyright:
                if isinstance(copyr, nltk.tree.Tree):
                    logger.debug('n: ' + str(copyr))
                    node_text = CopyrightDetector.as_str(copyr)
                    if 'YR-RANGE' in (copyr.label() if nltk3 else copyr.node):
                        years.append(refine_date(node_text))
                    elif ('NAME' == (copyr.label() if nltk3 else copyr.node)
                          or 'COMPANY' in (copyr.label() if nltk3 else copyr.node)):
                        # FIXME : this would wreck things like 23andme
                        # where a company name contains numbers
                        holders.append(refine_author(node_text))
                        logger.debug('CopyrightDetector: node_text: ' + node_text)
                    collect_year_and_holder(copyr)

        # then walk the parse tree, collecting copyrights, years and authors
        for tree_node in tree:
            if isinstance(tree_node, nltk.tree.Tree):
                node_text = CopyrightDetector.as_str(tree_node)
                if 'COPYRIGHT' in (tree_node.label() if nltk3 else tree_node.node):
                    if node_text and node_text.strip():
                        refined = refine_copyright(node_text)
                        if not is_junk(refined):
                            copyrights.append(refined)
                            collect_year_and_holder(tree_node)
                elif (tree_node.label() if nltk3 else tree_node.node) == 'AUTHOR':
                    authors.append(refine_author(node_text))

        return copyrights, authors, years, holders, start_line, end_line

    def get_tokens(self, numbered_lines):
        """
        Return an iterable of tokens from lines of text.
        """
        tokens = []
        # simple tokenization: spaces and some punctuation
        splitter = re.compile('[\\t =;]+')

        for _line_number, line in numbered_lines:
            line = line.strip()
            if line:
                line = prepare_text_line(line)
            if line :
                line = strip_markup(line)
            if line and line.strip():
                for tok in splitter.split(line):
                    # strip trailing quotes and ignore empties
                    tok = tok.strip("' ")
                    if not tok:
                        continue
                    # strip trailing colons: why?
                    tok = tok.rstrip(':').strip()
                    # strip leading @: : why?
                    tok = tok.lstrip('@').strip()
                    if tok and tok not in (':',):
                        tokens.append(tok)
        logger.debug('CopyrightDetector:tokens: ' + repr(list(tokens)))
        return tokens


def is_candidate(line):
    """
    Return True if a line is a candidate line for copyright detection
    """
    line = line.lower()
    line = prepare_text_line(line)
    return (has_content(line)
            and any(s in line for s in copyrights_hint.statement_markers))


def has_content(line):
    """
    Return True if a line has some content, ignoring white space, digit and
    punctuation.
    """
    return re.sub(r'\W+', '', line)


def is_all_rights_reserved(line):
    """
    Return True if a line ends with "all rights reserved"-like statements.
    """
    line = prepare_text_line(line)
    # remove any non-character
    line = re.sub(r'\W+', '', line)
    line = line.strip()
    line = line.lower()
    return line.endswith(('rightreserved', 'rightsreserved'))


def candidate_lines(lines):
    """
    Yield lists of candidate lines where each list element is a tuple of
    (line number,  line text).

    A candidate line is a line of text that may contain copyright statements.
    A few lines before and after a candidate line are also included.
    """
    candidates = deque()
    previous = None
    # used as a state and line counter
    in_copyright = 0
    for line_number, line in enumerate(lines):
        # the first line number is ONE, not zero
        numbered_line = (line_number + 1, line)
        if is_candidate(line):
            # the state is now "in copyright"
            in_copyright = 2
            # we keep one line before a candidate line if any
            if previous:
                candidates.append(previous)
                previous = None
            # we keep the candidate line and yield if we reached the end
            # of a statement
            candidates.append(numbered_line)
            if is_all_rights_reserved(line):
                yield list(candidates)
                candidates.clear()
                in_copyright = 0
        else:
            if in_copyright:
                # if the previous line was a candidate
                # then we keep one line after that candidate line
                if has_content(line):
                    candidates.append(numbered_line)
                    # and decrement our state
                    in_copyright -= 1
                else:
                    if candidates:
                        yield list(candidates)
                        candidates.clear()
                    in_copyright = 0
            else:
                # if are neither a candidate line nor the line just after
                # then we yield the accumulated lines if any
                if candidates:
                    yield list(candidates)
                    candidates.clear()
                # and we keep track of this line as "previous"
                if has_content(line):
                    previous = numbered_line
                else:
                    previous = None
    # finally
    if candidates:
        yield list(candidates)


def strip_markup(text):
    """
    Strip markup tags from text.
    """
    html_tag_regex = re.compile(
        r'<'
        r'[(--)\?\!\%\/]?'
        r'[a-zA-Z0-9#\"\=\s\.\;\:\%\&?!,\+\*\-_\/]+'
        r'\/?>',
        re.MULTILINE | re.UNICODE
    )
    if text:
        text = re.sub(html_tag_regex, ' ', text)
    return text


COMMON_WORDS = set([
    'Unicode',
    'Modified',
    'NULL',
    'FALSE', 'False',
    'TRUE', 'True',
    'Last',
    'Predefined',
    'If',
    'Standard',
    'Version', 'Versions',
    'Package', 'PACKAGE',
    'Powered',
    'Licensed', 'License', 'License.' 'Licensee', 'License:', 'License-Alias:',
    'Legal',
    'Entity',
    'Indemnification.',
    'AS', 'IS',
    'See',
    'This',
    'Java',
    'DoubleClick',
    'DOM', 'SAX', 'URL',
    'Operating System',
    'Original Software',
    'Berkeley Software Distribution',
    'Software Release', 'Release',
    'IEEE Std',
    'BSD',
    'POSIX',
    'Derivative Works',
    'Intellij IDEA',
    'README', 'NEWS',
    'ChangeLog', 'CHANGElogger', 'Changelog',
    'Redistribution',
])


def lowercase_well_known_word(text):
    """
    Return text with certain words lowercased.
    Rationale: some common words can start with a capital letter and be mistaken
    for a named entity because capitalized words are often company names.
    """
    lines = []
    for line in text.splitlines(True):
        words = []
        for word in line.split():
            if word in COMMON_WORDS:
                word = word.lower()
            words.append(word)
        lines.append(' '.join(words))
    return '\n'.join(lines)


# FIXME: instead of using functions, use plain re and let the re cache do its work

def IGNORED_PUNCTUATION_RE():
    return re.compile(r'[*#"%\[\]\{\}`]+', re.I | re.M | re.U)

def ASCII_LINE_DECO_RE():
    return re.compile(r'[-_=!\\*]{2,}')

def ASCII_LINE_DECO2_RE():
    return re.compile(r'/{3,}')

def WHITESPACE_RE():
    return re.compile(r' +')

def MULTIQUOTES_RE():
    return re.compile(r"\'{2,}")

# TODO: add debian <s> </s> POS name taggings
def DEBIAN_COPYRIGHT_TAGS_RE():
    return re.compile(r"(\<s\>|\<s\\/>)")


def prepare_text_line(line):
    """
    Prepare a line of text for copyright detection.
    """

    # FIXME: maintain the original character positions

    # strip whitespace
    line = line.strip()

    # strip comment markers
    # common comment characters
    line = line.strip('\\/*#%;')
    # un common comment line prefix in dos
    line = re.sub('^rem ', ' ', line)
    line = re.sub('^\@rem ', ' ', line)
    # un common comment line prefix in autotools am/in
    line = re.sub('^dnl ', ' ', line)
    # un common comment line prefix in man pages
    line = re.sub('^\.\\"', ' ', line)
    # un common pipe chars in some ascii art
    line = line.replace('|', ' ')

    # normalize copyright signs and spacing aournd them
    line = line.replace('(C)', ' (c) ')
    line = line.replace('(c)', ' (c) ')
    # the case of \251 is tested by 'weirdencoding.h'
    line = line.replace(u'\251', u' (c) ')
    line = line.replace('&copy;', ' (c) ')
    line = line.replace('&#169;', ' (c) ')
    line = line.replace('&#xa9;', ' (c) ')
    line = line.replace(u'\xa9', ' (c) ')
    # FIXME: what is \xc2???
    line = line.replace(u'\xc2', '')

    # TODO: add more HTML entities replacements
    # see http://www.htmlhelp.com/reference/html40/entities/special.html
    # convert html entities &#13;&#10; CR LF to space
    line = line.replace(u'&#13;&#10;', ' ')
    line = line.replace(u'&#13;', ' ')
    line = line.replace(u'&#10;', ' ')

    # normalize (possibly repeated) quotes to unique single quote '
    # backticks ` and "
    line = line.replace(u'`', "'")
    line = line.replace(u'"', "'")
    line = re.sub(MULTIQUOTES_RE(), "'", line)
    # quotes to space?  but t'so will be wrecked
    # line = line.replace(u"'", ' ')

    # some trailing garbage ')
    line = line.replace("')", '  ')


    # note that we do not replace the debian tag by a space:  we remove it
    line = re.sub(DEBIAN_COPYRIGHT_TAGS_RE(), '', line)

    line = re.sub(IGNORED_PUNCTUATION_RE(), ' ', line)

    # tabs to spaces
    line = line.replace('\t', ' ')

    # normalize spaces around commas
    line = line.replace(' , ', ', ')

    # remove ASCII "line decorations"
    # such as in --- or === or !!! or *****
    line = re.sub(ASCII_LINE_DECO_RE(), ' ', line)
    line = re.sub(ASCII_LINE_DECO2_RE(), ' ', line)

    # Replace escaped literal \0 \n \r \t that may exist as-is by a space
    # such as in code literals: a="\\n some text"
    line = line.replace('\\r', ' ')
    line = line.replace('\\n', ' ')
    line = line.replace('\\t', ' ')
    line = line.replace('\\0', ' ')

    # TODO: Why?
    # replace contiguous spaces with only one occurrence
    # line = re.sub(WHITESPACE_RE(), ' ', text)

    # normalize to ascii text
    line = commoncode.text.toascii(line)
    # logger.debug("ascii_only_text: " + text)

    # strip verbatim back slash and comment signs again at both ends of a line
    # FIXME: this is done at the start of this function already
    line = line.strip('\\/*#%;')

    # normalize to use only LF as line endings so we can split correctly
    # and keep line endings
    line = commoncode.text.unixlinesep(line)
    # why?
    line = lowercase_well_known_word(line)

    return line
