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

from __future__ import absolute_import, division, print_function

from functools import partial
from itertools import chain
import re
import textwrap

from licensedcode import query
from licensedcode.tokenize import rule_pattern
from licensedcode.tokenize import query_pattern

"""
Collect matched texts in query and rule files or strings.
"""


def get_texts(match, location=None, query_string=None, idx=None):
    """
    Given a match and a query location of query string return a tuple of:
    - the matched query text as a string.
    - the matched rule text as a string.

    Used primarily to recover the matched texts for testing or reporting.

    Unmatched positions are represented as <no-match>, rule gaps as <gap>. 
    Initial formatting is preserved. 
    """
    assert idx
    return (get_matched_qtext(match, location, query_string, idx),
            get_match_itext(match))


def get_matched_qtext(match, location=None, query_string=None, idx=None):
    """
    Return the matched query text given a match, a query location or string and
    an index dictionary.

    Used primarily to recover the matched texts for testing or reporting.

    Unmatched positions are represented as <no-match>.
    Punctuation is removed , spaces are normalized (new line is replaced by a
    space), case is preserved. 

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    assert idx
    tokens = matched_query_tokens_str(match, location, query_string, idx)
    return format_text(tokens, width)


def get_match_itext(match, width=120):
    """
    Return the matched rule text as a wrapped string of `width` given a match
    and an index dictionary.

    Used primarily to recover the matched texts for testing or reporting.

    Unmatched positions inside a matched region are represented as <no-match>
    and rule gaps as <gap>.

    Punctuation is removed , spaces are normalized (new line is replaced by a
    space), case is preserved. 

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    return format_text(matched_rule_tokens_str(match), width)


def format_text(tokens, width=120, no_match='<no-match>'):
    """
    Return a formatted text wrapped at `width` given an iterable of tokens.
    None tokens for unmatched positions are replaced with `no_match`. 
    """
    nomatch = lambda s: s or no_match
    noop = lambda x: x
    wrapper = partial(textwrap.wrap, width=width, break_on_hyphens=False)
    wrap = width and wrapper or noop
    tokens = map(nomatch, tokens)
    return u'\n'.join(wrap(u' '.join(tokens)))


def build_text(tokens, span, template=u'<%s>'):
    text = []
    for is_tok, tok_pos, tok in tokens:
        if not is_tok:
            text.append(tok)
        else:
            if tok_pos in span:
                text.append(tok)
            else:
                text.append(template % tok)


query_strings = re.compile(query_pattern , re.UNICODE | re.VERBOSE).finditer

def query_tokens(query_text):
    """
    Return an iterable of three-tuples describing the strings of a query text
    including tokens and non-tokens:
    
    - is_token  = True if the string is for a valid token (False for spaces,etc)
    - token position =  use the tokenize conventions. Only valid if is_token.
    - string = the corresponding string whether this is a token or not.

    For example:
    >>> s = 'This  is. Not\\n\\n. !'
    >>> list(query_tokens(s))
    [(False, 0, ''), (True, 0, 'This'), (False, 1, '  '), (True, 1, 'is'), (False, 2, '. '), (True, 2, 'Not'), (False, 2, '\\n\\n. !')]

    """
    i = 0
    for pos, m in enumerate(query_strings(query_text)):
        yield False, pos, query_text[i:m.start()]
        # same as s[m.start():m.end()]
        yield True, pos, m.group()
        i = m.end()
    if i != (len(query_text) - 1):
        yield False, pos, query_text[m.end():]


rule_strings = re.compile(rule_pattern , re.UNICODE | re.VERBOSE).finditer

def rule_tokens(rule_text):
    """
    Return an iterable of three-tuples describing the strings of a rule text
    including tokens and non-tokens:

    - is_token  = True if the string is for a valid token (False for spaces,etc)
    - token position =  use the tokenize conventions. Only valid if is_token.
    - string = the corresponding string whether this is a token or not.

    For example:
    >>> s = 'This  is{{some te}}. Not\\n\\n. !'
    >>> res = list(rule_tokens(s))
    >>> ''.join(t[2] for t in res) == s
    True
    >>> ' '.join(t[2] for t in res if t[0]) == 'This is Not'
    True
    >>> res
    [(False, 0, ''), (True, 0, 'This'), (False, 1, '  '), (True, 1, 'is'), (False, 2, ''), (False, 2, '{{some te}}'), (False, 2, '. '), (True, 2, 'Not'), (False, 3, '\\n\\n. !')]
    """
    i = 0
    pos = 0
    for m in rule_strings(rule_text):
        yield False, pos, rule_text[i:m.start()]
        # same as s[m.start():m.end()]
        s = m.group()
        if s.startswith(u'{{'):
            yield False, pos, s
        else:
            yield True, pos, s
            pos += 1
        i = m.end()
    if i != (len(rule_text) - 1):
        yield False, pos, rule_text[m.end():]
