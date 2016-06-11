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

from __future__ import print_function, absolute_import

from array import array
from collections import namedtuple

from licensedcode import MAX_GAP_SKIP
from licensedcode import NGRAM_LENGTH
from licensedcode.match import LicenseMatch
from licensedcode.tokenize import rule_multigrams
from licensedcode.whoosh_spans.spans import Span


"""
Matching strategy using mapping of ngrams to rules positions where these ngrams
are found in a rule then doing a sequence alignment fomr that seed.

The idea is to find the leftmost matching ngrams and then match sequences of
tokens by looking left and right from that ngram for contiguous or non-
contiguous sequences that are in position order of the query and index,
eventually dealing with known rule gaps.

This is similar to the approach of Python's difflib SequenceMatcher and the
approach of most diff tools: the difference is that they are computing for the
longest common sequence first. Here we use the ngram as a proxy for the LCS and
do not compute the LCS.

Using such an indexed "seed" instead of an LCS is essentially the high level
strategy of BLAST, a tool and algorithm for genome and protein sequences
alignment. 

Unlike a diff, we shortcut computing the longest contiguous sequence using
ngrams as proxies (or as seeds using BLAST jargon), hoping the ngram guided us
somewhere inside the earliest and longest matching sequence leading to a good
alignment. This may not always produce the optimal alignment nor the best
looking alignment but this is a good enough and much faster approximation.

For this we first lookup an ngram, then we loop as long as the query and index
token match. When a ngram is found we always start by looking the earliest
position of that ngram in the index rule.

For instance, we can match a whole unmodified license text in one pass without
needing further matching or alignment.

For that we index for each rule the ngrams mapped to their start position.

At matching time:
 - compute ngrams from the query.
 - lookup ngrams in the index for ngrams.
 -- If there is a hit, match as far as possible from that point left and right
 -- yield a LicenseMatch 
"""

"""
To consider:
BLAST
difflib
Various LCSess
http://wordaligned.org/articles/longest-common-subsequence
http://wordaligned.org/articles/longest-common-subsequence.html

http://hamilton.nuigalway.ie/teachingWeb/CompMolBio/LCS.py
biopython
http://rosettacode.org/wiki/Longest_common_subsequence#Greedy_Algorithm
http://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_7
http://www.algorithmist.com/index.php/Longest_Common_Subsequence 

https://pypi.python.org/pypi/py_common_subseq/
https://en.wikipedia.org/wiki/Longest_common_subsequence_problem
https://github.com/man1/Python-LCS/blob/master/lcs.py

and http://stackoverflow.com/questions/24735382/fast-multiset-containment-of-lists-in-python
https://pypi.python.org/pypi/Banyan
"""

# Set to False to enable debug tracing
TRACE = False
TRACE_CHUNK = False
TRACE_CHUNK_DEEP = False

TRACE_EXTEND_DEEP = False
TRACE_EXTEND = False

TRACE_MG = False
TRACE_MG_DEEP = False
TRACE_MG_EXTEND = False

if TRACE or TRACE_EXTEND or TRACE_MG:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:
    def logger_debug(*args):
        pass


MATCH_MULTIG_TYPE = 'multigram_chunk'


# FIXME: this is NOT used
def index_multigrams(rule_tokens, gaps, len_junk, ngram_length=NGRAM_LENGTH):
    return [0] * (ngram_length + 1)


def index_multigrams_old(rule_tokens, gaps, len_junk, ngram_length=NGRAM_LENGTH):
    """
    Given an sequence of rule tokens and a set of gaps for that rule, return a
    mapping of ngram len -> (ngram -> [sorted start positions]) computed from
    the tokens, gaps and ngram len. start is the starting position of the ngram.
    """
    indexes = [0] * (ngram_length + 1)
    for start, nglen, ngram in rule_multigrams(rule_tokens, ngram_length=ngram_length, gaps=gaps, len_junk=len_junk):
        if not indexes[nglen]:
            indexes[nglen] = {}
        idx = indexes[nglen]
        if ngram not in idx:
            idx[ngram] = array('h', [])
        idx[ngram].append(start)
    return indexes


def match_chunks_multigrams(idx, candidates, query_run, with_gaps=True):
    """
    Return a LicenseMatch by matching the query_run against the idx index
    only for the `candidates` rule ids. 
    
    `candidates` is a list of candidate rule (ird, rule, intersection) sorted by
    decreasing likeliness of being matched. 
    """
    if TRACE_MG: logger_debug(' #match_chunk_multigrams: start ... with candidates:', len(candidates))
    if not candidates:
        return []

    len_junk = idx.len_junk
    ngram_length = idx.ngram_length

    line_by_pos = query_run.line_by_pos
    matchables = query_run.matchables

    qtokens = query_run.query.tokens
    qbegin = query_run.start
    qfinish = len(query_run.query.tokens) - 1

    if TRACE_MG_DEEP: logger_debug(' #match_chunk_multigrams: index:', idx.multigrams_by_rid, 'len_junk:', idx.len_junk)

    matches = []

    qr_multigrams = list(query_run.multigrams(ngram_length=ngram_length))
    for rid, rule, intersection in candidates:
        rid_multigrams = idx.multigrams_by_rid[rid]
        if not rid_multigrams:
            continue

        rule_matches = []
        if TRACE_MG: logger_debug('##match_chunk_multigrams: matching against rule:', rule)
        itokens = idx.tids_by_rid[rid]

        # all rules start at 0
        ibegin = 0
        ifinish = rule.length - 1

        gaps = rule.gaps
        thresholds = rule.thresholds()

        qspan_end = 0
        for qstart, qnglen, qngram in qr_multigrams:

            if TRACE_MG_DEEP: logger_debug(' #match_chunk_multigrams: searching QRY ngram:', repr(idx._tokens2text(qngram)), 'qstart:', qstart)
            if TRACE_MG: logger_debug(' #match_chunk_multigrams: searching QRY qstart, qnglen, qngram:', qstart, qnglen, qngram)

            slice_offset = qnglen + 1
            span_offset = qnglen - 1

            if qstart < qspan_end:
                continue
            # stop checking for this qngram if any of its positions matched
            if qstart not in matchables or any(p not in matchables for p in xrange(qstart, qstart + slice_offset)):
                if TRACE_MG: logger_debug(' #match_chunk_multigrams: > qngram not matchable')
                continue

            ispan_end = 0

            multigrams_for_len = rid_multigrams[qnglen]
            if not multigrams_for_len:
                continue

            for istart in multigrams_for_len.get(qngram, []):
                if istart < ispan_end:
                    continue

                if TRACE_MG: logger_debug('   match_chunk_multigrams: IDX ngram found at istart:', istart, ' for matching itokens:', repr(idx._tokens2text(itokens[istart: istart + slice_offset])))
                if TRACE_MG_DEEP: logger_debug('     match_chunk_multigrams: IDX ngram found at qstart:', qstart, ' for matching qtokens:', repr(idx._tokens2text(qtokens[qstart: qstart + slice_offset])))

                if TRACE_MG_DEEP: assert array('h', qtokens[qstart: qstart + slice_offset]) == itokens[istart: istart + slice_offset]

                # initial matched Span of ngram_length
                qspan = Span(qstart, qstart + span_offset)
                ispan = Span(istart, istart + span_offset)

                if TRACE_MG_DEEP: logger_debug('     ##match_chunk_multigrams: initial qspan: ', qspan, 'qtext:', idx._tokens2text(_span2tokens(qspan, qtokens)))
                if TRACE_MG_DEEP: logger_debug('     ##match_chunk_multigrams: initial ispan: ', ispan, 'itext:', idx._tokens2text(_span2tokens(ispan, itokens)))

                # extend matched ngram left and right
                qsequence = Sequence2(tokens=qtokens, begin=qbegin, finish=qfinish, start=qstart, end=qstart + span_offset)
                isequence = Sequence2(tokens=itokens, begin=ibegin, finish=ifinish, start=istart, end=istart + span_offset)

                qspan, ispan = extend_multigrams(qsequence, isequence, qspan, matchables, ispan, gaps, thresholds, with_gaps=with_gaps, _tk2tx=idx._tokens2text)

                # qspan_end, ispan_end = qspan.end, ispan.end
                if TRACE_MG_DEEP: logger_debug('      ##match_chunk_multigrams: extended qspan: ', qspan, 'qtext:', idx._tokens2text(_span2tokens(qspan, qtokens)))
                if TRACE_MG_DEEP: logger_debug('      ##match_chunk_multigrams: extended ispan: ', ispan, 'itext:', idx._tokens2text(_span2tokens(ispan, itokens)))

                # FIXME: this could/should be pre-computed and stored with the ngram
                hispan = Span(p for p in ispan if itokens[p] >= len_junk)
                # finally create a match, possibly as small as the ngram if no extension was possible
                match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, MATCH_MULTIG_TYPE)
                rule_matches.append(match)

                # matches cannot overlap
                query_run.subtract(match.qspan)

                if TRACE_MG_DEEP: logger_debug('   #match_chunk_multigrams:', match)

        matches.extend(LicenseMatch.merge(rule_matches, max_dist=MAX_GAP_SKIP))

        if not query_run.high_matchables:
            break

    if TRACE_MG:
        logger_debug('match_chunk_multigrams: matches found#', len(matches))
        if TRACE_MG_DEEP: map(logger_debug, matches)

    return matches


def _span2tokens(span, tokens):
    return [tokens[p] for p in sorted(span)]


"""
Sequence of tokens with a range of tokens already matched:
 - whole tokens sequence
 - begin and finish positions in the whole tokens sequence
 - start and end positions already matched in the whole tokens sequence
"""
Sequence2 = namedtuple('Sequence', 'tokens begin finish start end')


# @profile
def extend_multigrams(qsequence, isequence, qspan, matchables, ispan, gaps, thresholds, with_gaps=True, _tk2tx=None):
    """
    Return the extended `qspan` and `ispan` Spans updating them in-place given:
    - initial matched sequences `qsequence` and `isequence`,
    - 
    The sequences are extended left and right for matching tokens considering the gaps and thresholds.

    `_tk2tx` is an optional tracing callable returning the text of a token ids sequence. 
    """

    qtokens, qbegin, qfinish, qstart, qend = qsequence
    itokens, ibegin, ifinish, istart, iend = isequence

    low_matchables, high_matchables = matchables
    thresholds_small = thresholds.small
    thresholds_max_gap_skip = thresholds.max_gap_skip

    qspan_add = qspan.add
    ispan_add = ispan.add

    lgaps_skipped = 0
    # Extend to the left of the ngram for matching tokens
    while qstart > qbegin and istart > ibegin:
        qprev = qstart - 1
        iprev = istart - 1
        if TRACE_MG_EXTEND: logger_debug('         >> right: qend:', qend, 'qfinish:', qfinish, 'iend:', iend, 'ifinish:', ifinish,)
        if qtokens[qprev] != itokens[iprev]:
            if TRACE_MG_EXTEND: logger_debug('         >> NOT EQUAL extend left: qend:', qend, 'iend:', istart - 1, 'tok:', repr(_tk2tx([qtokens[qend]])))
            if not with_gaps:
                if TRACE_MG_EXTEND: logger_debug('         >>>  NO GAP extend left')
                break
            if thresholds_small:
                if iprev not in gaps or lgaps_skipped > thresholds_max_gap_skip:
                    if TRACE_MG_EXTEND: logger_debug('         >>>  NO GAP extend left')
                    break
                qstart = qprev
                lgaps_skipped += 1
                if TRACE_MG_EXTEND: logger_debug('         >>>  GAP for small extend left')
                continue
            if iprev in gaps:
                qstart = qprev
                lgaps_skipped = 0
                if TRACE_MG_EXTEND: logger_debug('         >>>  GAP extend left')
                continue
            if lgaps_skipped > thresholds_max_gap_skip:
                if TRACE_MG_EXTEND: logger_debug('         >>>  NO GAP extend left')
                break

            qstart = qprev
            lgaps_skipped += 1
            if TRACE_MG_EXTEND: logger_debug('         >>>  GAP extend left')
            continue

        # here qtokens[qprev] == itokens[iprev]
        lgaps_skipped = 0
        if qprev in high_matchables or qprev in low_matchables:
            qspan_add(qprev)
            ispan_add(iprev)
            if TRACE_MG_EXTEND: logger_debug('         >> extend left: qend:', qend, 'iend:', istart - 1, 'tok:', repr(_tk2tx([qtokens[qend]])))

        qstart = qprev
        istart = iprev

    # qend is already matched
    qend += 1
    iend += 1
    rgaps_skipped = 0

    # ... then extend right of the ngram for matching tokens
    while qend <= qfinish and iend <= ifinish:
        if TRACE_MG_EXTEND: logger_debug('         >> right: qend:', qend, 'qfinish:', qfinish, 'iend:', iend, 'ifinish:', ifinish,)
        if qtokens[qend] != itokens[iend]:
            if TRACE_MG_EXTEND: logger_debug('         >> NOT EQUAL extend right: qend:', qend, 'iend:', iend, 'tok:', repr(_tk2tx([qtokens[qend]])))
            if not with_gaps:
                break
            if thresholds_small:
                if iend - 1 not in gaps or rgaps_skipped > thresholds_max_gap_skip:
                    if TRACE_MG_EXTEND: logger_debug('         >>>  NO GAP extend right')
                    break
                qend += 1
                rgaps_skipped += 1
                if TRACE_MG_EXTEND: logger_debug('         >>>  GAP for small extend right')
                continue
            if iend - 1 in gaps:
                qend += 1
                rgaps_skipped = 0
                if TRACE_MG_EXTEND: logger_debug('         >>>  GAP extend right')
                continue

            if rgaps_skipped > thresholds_max_gap_skip:
                if TRACE_MG_EXTEND: logger_debug('         >>>  NO GAP extend right')
                break

            qend += 1
            rgaps_skipped += 1
            if TRACE_MG_EXTEND: logger_debug('         >>>  GAP extend right')
            continue

        # here qtokens[qend] == itokens[iend]
        rgaps_skipped = 0
        if qend in high_matchables or qend in low_matchables:
            qspan_add(qend)
            ispan_add(iend)
            if TRACE_MG_EXTEND: logger_debug('         >> extend right: qend:', qend, 'iend:', iend, 'tok:', repr(_tk2tx([qtokens[qend]])))

        qend += 1
        iend += 1
    return qspan, ispan


def match_chunks(idx, candidate, query_run, with_gaps=True):
    """
    Return a list of LicenseMatch by matching the query sequence against the idx
    index, for a `candidate` tuple of (rid, rule, multiset intersection).

    If `with_gaps` return matches that may include gaps in their matched
    sequence. Otherwise only return contiguous matches.
    """
    rid, rule, intersection = candidate

    TRACE_CHUNK = False
    _DEBUG = False
    _DEBUG_DEEP = False
    if rule.identifier == 'bsd-new_29.RULE':
        TRACE_CHUNK = True
        _DEBUG = True
        _DEBUG_DEEP = True

    if TRACE_CHUNK: logger_debug(' #match_chunks: start ... with candidate:', rule)

    len_junk = idx.len_junk
    line_by_pos = query_run.line_by_pos
    low_matchables = query_run.low_matchables
    high_matchables = query_run.high_matchables

    # we look at the whole query sequence, not a slice: WHY???
    # qtokens = query_run.query.tokens
    qtokens = query_run.query.tokens

    qbegin = query_run.start
    # if we want to extend past the current run end, use instead: qfinish = len(query_run.query.tokens) - 1
    qfinish = query_run.end

    gaps = rule.gaps
    thresholds = rule.thresholds()
    itokens = idx.tids_by_rid[rid]
    ibegin = 0
    ifinish = rule.length - 1

    rule_matches = []

    qpos = qbegin
    while qpos <= qfinish:
        if not high_matchables:
            if TRACE_CHUNK: logger_debug(' #match_chunks: not query_run.high_matchables for qtoken:', repr(idx._tokens2text([qtokens[qpos]])), 'qpos:', qpos)
            break

        qtoken = qtokens[qpos]
        if TRACE_CHUNK: logger_debug(' #match_chunks: processing qtoken:', repr(idx._tokens2text([qtoken])), 'qpos:', qpos)

        if qtoken < len_junk or qpos not in high_matchables or not intersection[qtoken]:
            # also deals with None or -1 tokens
            if TRACE_CHUNK: logger_debug('   #match_chunks: skip junk or not matchable qtoken')
            qpos += 1
            continue

        ipos = ibegin
        while ipos <= ifinish:
            itoken = itokens[ipos]

            if TRACE_CHUNK: logger_debug('   #match_chunks: searching itoken:', repr(idx._tokens2text([itoken])), 'ipos:', ipos)

            if itoken < len_junk or not intersection[itoken]:
                # also deals with None or -1 tokens
                if TRACE_CHUNK: logger_debug('   #match_chunks: skip junk itoken')
                ipos += 1
                continue

            if qtoken == itoken and intersection[itoken] and (qpos in high_matchables or qpos in low_matchables):
            # and qtoken >= len_junk:
                if TRACE_CHUNK: logger_debug('    #match_chunks: qtoken == itoken')


                qsequence, isequence = Sequence(qtokens, qbegin, qfinish, qpos), Sequence(itokens, ibegin, ifinish, ipos)
                qspan, ispan = extend(qsequence, isequence, low_matchables, high_matchables, intersection, gaps, thresholds,
                                      with_gaps=with_gaps, _tk2tx=idx._tokens2text,
                                      _DEBUG=_DEBUG, _DEBUG_DEEP=_DEBUG_DEEP)

                if TRACE_CHUNK_DEEP: logger_debug('      ##match_chunks: extended qspan: ', qspan, 'qtext:', idx._tokens2text(_span2tokens(qspan, qtokens)))
                if TRACE_CHUNK_DEEP: logger_debug('      ##match_chunks: extended ispan: ', ispan, 'itext:', idx._tokens2text(_span2tokens(ispan, itokens)))

                hispan = Span(p for p in ispan if itokens[p] >= len_junk)

                match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, MATCH_MULTIG_TYPE)
                if TRACE_CHUNK: logger_debug('   #match_chunks: MATCH', match)

                rule_matches.append(match)
                query_run.subtract(match.qspan)

                ispan_end = ispan.end
                if ispan_end < ifinish:
                    ipos = ispan_end + 1
                else:
                    break

                qspan_end = qspan.end
                if qspan_end < qfinish:
                    qpos = qspan_end + 1
                    qtoken = qtokens[qpos]
                else:
                    qpos = qspan_end
                    break
            else:
                ipos += 1

        if qpos > qfinish:
            break
        qpos += 1

    if TRACE and rule_matches:
        logger_debug('match_chunks: matches found#', len(rule_matches))
        logger_debug('match_chunks: matches found#', rule_matches)

    return rule_matches



"""
Sequence of tokens with a range of tokens already matched:
 - whole tokens sequence
 - begin and finish positions in the whole tokens sequence
 - start positions already matched in the whole tokens sequence
"""
Sequence = namedtuple('Sequence', 'tokens begin finish start_pos')


# @profile
def extend(qsequence, isequence, low_matchables, high_matchables, intersection, gaps, thresholds, with_gaps=True, 
           _tk2tx=None, _DEBUG=False, _DEBUG_DEEP=False):
    """
    Return a `qspan` and `ipositions` Spans of aligned positions given sequences
    `qsequence` and `isequence` (including a match start position), the low &
    high matchables, the multisets intersection, the rule gaps and rule thresholds.
    
    The sequences are extended left and right for matching tokens considering
    the gaps and thresholds. 

    If `with_gaps` extend over non matching tokens. Otherwise stop extending
    when a qtoken and itoken differ, meaning that we only consider contiguous
    sequences.
    
    `_tk2tx` is an optional tracing callable returning the text of a token ids
    sequence.
    """
    qtokens, qbegin, qfinish, qstart_pos = qsequence
    itokens, ibegin, ifinish, istart_pos = isequence
    qpositions, ipositions = [qstart_pos], [istart_pos]
    qpositions_append, ipositions_append = qpositions.append, ipositions.append
    thresholds_small = thresholds.small
#     thresholds_max_gap_skip = 15  # if thresholds_small else 10 #thresholds.max_gap_skip
    thresholds_max_gap_skip = thresholds.max_gap_skip
    if not thresholds_max_gap_skip:
        with_gaps = False

    if qstart_pos < qbegin or qfinish < qstart_pos or istart_pos < ibegin or ifinish < istart_pos:
        return Span(qpositions), Span(ipositions)

    # Extend to the left for matching tokens
    qpos = qstart_pos - 1
    ipos = istart_pos - 1
    skipped = 0
    if _DEBUG and (qpos < qbegin or ipos < ibegin): logger_debug('       >> NOT considering extending left for qpos:', qpos, 'ipos:', ipos,)

    while qpos >= qbegin and ipos >= ibegin:
        if _DEBUG: logger_debug('       >> extending left for: qpos:', qpos, 'qfinish:', qfinish, 'ipos:', ipos, 'ifinish:', ifinish)
        qtoken = qtokens[qpos]
        if _DEBUG_DEEP: logger_debug('       >> extending left for: token', repr(_tk2tx([qtoken])), 'qpos:', qpos, 'qfinish:', qfinish, 'ipos:', ipos, 'ifinish:', ifinish)

        if qtoken != itokens[ipos]:
            if _DEBUG_DEEP: logger_debug('         >> NOT EQUAL in extend left')

            if (not with_gaps) or skipped > thresholds_max_gap_skip or (thresholds_small and ipos not in gaps):
                if _DEBUG_DEEP:
                    if not with_gaps: logger_debug('           >>>  Not with_gap. Stop extend left')
                    if skipped > thresholds_max_gap_skip: logger_debug('           >>>  Reached max gap. Stop extend left')
                    if thresholds_small and ipos not in gaps: logger_debug('           >>>  Small: not a gap. Stop extend left')
                break

            if ipos in gaps:
                if _DEBUG_DEEP: logger_debug('           >>>  GAP continue left')
                qpos -= 1
                skipped = 0
                continue

            if qtoken is None:
                if _DEBUG_DEEP: logger_debug('           >>>  None: continue left')
                qpos -= 1
                skipped += 1
                continue

            if _DEBUG_DEEP: logger_debug('           >>>  No gap, continue left')
            qpos -= 1
            skipped += 1
            continue

        # here qtokens[qpos] == itokens[ipos]
        if _DEBUG_DEEP: logger_debug('         >> EQUAL in extend left')
        skipped = 0
        if intersection[qtoken] and qpos in low_matchables or qpos in high_matchables:
            if _DEBUG: logger_debug('          >> extend left: EXTENDING equal')
            qpositions_append(qpos)
            ipositions_append(ipos)

        qpos -= 1
        ipos -= 1

    # Extend to the right for matching tokens
    qpos = qstart_pos + 1
    ipos = istart_pos + 1

    # shortcut to return early if there no possibility to extend right
    if qpos < qbegin or qpos > qfinish or ipos < ibegin or ipos > ifinish:
        return Span(qpositions), Span(ipositions)

    skipped = 0
    if _DEBUG and qpos <= qfinish and ipos <= ifinish: logger_debug('       >> NOT considering extending right for qpos:', qpos, 'ipos:', ipos,)
    while qpos <= qfinish and ipos <= ifinish:
        qtoken = qtokens[qpos]
        if _DEBUG: logger_debug('       >> extending right for: token', repr(_tk2tx([qtoken])), 'qpos:', qpos, 'qfinish:', qfinish, 'ipos:', ipos, 'ifinish:', ifinish,)

        if qtoken != itokens[ipos]:
            if _DEBUG_DEEP: logger_debug('         >> NOT EQUAL in extend right')

            if (not with_gaps) or skipped > thresholds_max_gap_skip or (thresholds_small and ipos - 1 not in gaps):
                if _DEBUG_DEEP:
                    if not with_gaps: logger_debug('           >>>  Not with_gap. Stop extend right')
                    if skipped > thresholds_max_gap_skip: logger_debug('           >>>  Reached max gap. Stop extend right')
                    if thresholds_small and ipos - 1 not in gaps: logger_debug('           >>>  Small: not a gap. Stop extend right')
                break

            if ipos - 1 in gaps:
                if _DEBUG_DEEP: logger_debug('           >>>  GAP continue right')
                qpos += 1
                skipped = 0
                continue

            if qtoken is None:
                if _DEBUG_DEEP: logger_debug('           >>>  None: continue right')
                qpos += 1
                skipped += 1
                continue

            if _DEBUG_DEEP: logger_debug('           >>>  No gap, continue right')
            qpos += 1
            skipped += 1
            continue

        # here qtokens[qpos] == itokens[ipos]
        if _DEBUG_DEEP: logger_debug('         >> EQUAL in extend right')
        skipped = 0
        if intersection[qtoken] and qpos in low_matchables or qpos in high_matchables:
            if _DEBUG: logger_debug('          >> extend right: EXTENDING equal')
            qpositions_append(qpos)
            ipositions_append(ipos)

        qpos += 1
        ipos += 1

    return Span(qpositions), Span(ipositions)
