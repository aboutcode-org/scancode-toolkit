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

from collections import namedtuple

from licensedcode.match import LicenseMatch
from licensedcode.whoosh_spans.spans import Span
from array import array


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
TRACE_SMALL = False
TRACE_MG = False
TRACE_EXTEND = False
TRACE_EXTEND_DEEP = False
TRACE_DEEP = False
TRACE_MG_DEEP = False


if TRACE or TRACE_EXTEND or TRACE_MG:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:
    def logger_debug(*args):
        pass


def _span2tokens(span, tokens):
    return [tokens[p] for p in sorted(span)]


def match_chunks(idx, candidate, query_run, with_gaps=True):
    """
    Return a list of LicenseMatch by matching the query sequence against the idx
    index, for a `candidate` tuple of (rid, rule, multiset intersection).

    If `with_gaps` return matches that may include gaps in their matched
    sequence. Otherwise only return contiguous matches.
    """
    rid, rule, intersection = candidate
    if TRACE_MG: logger_debug(' #match_chunks2: start ... with candidate:', rule)

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
            if TRACE_MG_DEEP: logger_debug(' #match_chunks2: not query_run.high_matchables for qtoken:', repr(idx._tokens2text([qtokens[qpos]])), 'qpos:', qpos)
            break

        if qpos not in high_matchables:
            if TRACE_MG_DEEP: logger_debug('   #match_chunks2: skip junk or not matchable qtoken')
            qpos += 1
            continue

        qtoken = qtokens[qpos]
        if TRACE_MG_DEEP: logger_debug(' #match_chunks2: processing qtoken:', repr(idx._tokens2text([qtoken])), 'qpos:', qpos)

        if qtoken < len_junk:  # or not intersection[qtoken]:
            # also deals with None or -1 tokens
            if TRACE_MG_DEEP: logger_debug('   #match_chunks2: skip junk or not matchable qtoken')
            qpos += 1
            continue

        if TRACE_MG: logger_debug(' #match_chunks2: searching qtoken:', repr(idx._tokens2text([qtoken])), 'qpos:', qpos)

        ipos = ibegin
        while ipos <= ifinish:
            itoken = itokens[ipos]

            if TRACE_MG_DEEP: logger_debug('   #match_chunks2: searching itoken:', repr(idx._tokens2text([itoken])), 'ipos:', ipos)

            if itoken < len_junk or not intersection[itoken]:
                # also deals with None or -1 tokens
                if TRACE_MG_DEEP: logger_debug('   #match_chunks2: skip junk itoken')
                ipos += 1
                continue

            if qtoken == itoken and qpos in high_matchables:  # or qpos in low_matchables):
                if TRACE_MG: logger_debug('    #match_chunks2: qtoken == itoken')

                qsequence, isequence = Sequence(qtokens, qbegin, qfinish, qpos), Sequence(itokens, ibegin, ifinish, ipos)
                qpositions, ipositions = extend(qsequence, isequence, low_matchables, high_matchables, gaps, thresholds,
                                      with_gaps=with_gaps, _tk2tx=idx._tokens2text)

                qspan, ispan = Span(qpositions), Span(ipositions)
                if TRACE_MG_DEEP: logger_debug('      ##match_chunks2: extended qspan: ', qspan, 'qtext:', idx._tokens2text(_span2tokens(qspan, qtokens)))
                if TRACE_MG_DEEP: logger_debug('      ##match_chunks2: extended ispan: ', ispan, 'itext:', idx._tokens2text(_span2tokens(ispan, itokens)))

                hispan = Span(p for p in ipositions if itokens[p] >= len_junk)


                match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, 'chunk')

                if match.small():
                    if TRACE_MG_DEEP: logger_debug('   #match_chunks2: match too small')
                    ipos += 1
                    continue

                if TRACE_MG_DEEP: logger_debug('   #match_chunks2: MATCH', match)

                rule_matches.append(match)
                query_run.subtract(match.qspan)

#                if not high_matchables:
#                    if TRACE_MG_DEEP: logger_debug(' #match_chunks2: not query_run.high_matchables for qtoken:', repr(idx._tokens2text([qtokens[qpos]])), 'qpos:', qpos)
#                    break

                ispan_end = ipositions[-1]
                if ispan_end < ifinish:
                    ipos = ispan_end + 1
                else:
                    break

                qspan_end = qpositions[-1]
                if qspan_end < qfinish:
                    qpos = qspan_end + 1
                    qtoken = qtokens[qpos]
                else:
                    qpos = qspan_end
                    break
            else:
                ipos += 1

        qpos += 1

    if TRACE and rule_matches:
        logger_debug('match_chunks2: matches found#', rule_matches)

    if TRACE_MG:
        logger_debug('match_chunks2: matches found#', len(rule_matches))
        if TRACE_MG_DEEP: map(logger_debug, rule_matches)

    return rule_matches


"""
Sequence of tokens with a range of tokens already matched:
 - whole tokens sequence
 - begin and finish positions in the whole tokens sequence
 - start positions already matched in the whole tokens sequence
"""
Sequence = namedtuple('Sequence', 'tokens begin finish start_pos')


# @profile
def extend(qsequence, isequence, low_matchables, high_matchables, gaps, thresholds, with_gaps=True, _tk2tx=None):
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
        return qpositions, ipositions

    # Extend to the left for matching tokens
    qpos = qstart_pos - 1
    ipos = istart_pos - 1
    skipped = 0
    if TRACE_EXTEND and (qpos < qbegin or ipos < ibegin): logger_debug('       >> NOT considering extending left for qpos:', qpos, 'ipos:', ipos,)

    while qpos >= qbegin and ipos >= ibegin:
        if TRACE_EXTEND: logger_debug('       >> extending left for: qpos:', qpos, 'qfinish:', qfinish, 'ipos:', ipos, 'ifinish:', ifinish)
        qtoken = qtokens[qpos]
        if TRACE_EXTEND_DEEP: logger_debug('       >> extending left for: token', repr(_tk2tx([qtoken])), 'qpos:', qpos, 'qfinish:', qfinish, 'ipos:', ipos, 'ifinish:', ifinish)

        if qtoken != itokens[ipos]:
            if TRACE_EXTEND_DEEP: logger_debug('         >> NOT EQUAL in extend left')

            if not with_gaps or skipped > thresholds_max_gap_skip:  # or (thresholds_small and ipos not in gaps):
                if TRACE_EXTEND_DEEP:
                    if not with_gaps: logger_debug('           >>>  Not with_gap. Stop extend left')
                    if skipped > thresholds_max_gap_skip: logger_debug('           >>>  Reached max gap. Stop extend left')
                    if thresholds_small and ipos not in gaps: logger_debug('           >>>  Small: not a gap. Stop extend left')
                break

            if ipos in gaps:
                if TRACE_EXTEND_DEEP: logger_debug('           >>>  GAP continue left')
                qpos -= 1
                skipped = 0
                continue

            if qtoken is None:
                if TRACE_EXTEND_DEEP: logger_debug('           >>>  None: continue left')
                qpos -= 1
                skipped += 1
                continue

            if TRACE_EXTEND_DEEP: logger_debug('           >>>  No gap, continue left')
            qpos -= 1
            skipped += 1
            continue

        # here qtokens[qpos] == itokens[ipos]
        if TRACE_EXTEND_DEEP: logger_debug('         >> EQUAL in extend left')
        skipped = 0
        # intersection[qtoken] and
        if qpos in low_matchables or qpos in high_matchables:
            if TRACE_EXTEND: logger_debug('          >> extend left: EXTENDING equal')
            qpositions_append(qpos)
            ipositions_append(ipos)

        qpos -= 1
        ipos -= 1

    # Extend to the right for matching tokens
    qpos = qstart_pos + 1
    ipos = istart_pos + 1

    # shortcut to return early if there no possibility to extend right
    if qpos < qbegin or qpos > qfinish or ipos < ibegin or ipos > ifinish:
        return qpositions, ipositions

    skipped = 0
    if TRACE_EXTEND:
        if qpos <= qfinish and ipos <= ifinish: logger_debug('       >> NOT considering extending right for qpos:', qpos, 'ipos:', ipos,)
    while qpos <= qfinish and ipos <= ifinish:
        qtoken = qtokens[qpos]
        if TRACE_EXTEND: logger_debug('       >> extending right for: token', repr(_tk2tx([qtoken])), 'qpos:', qpos, 'qfinish:', qfinish, 'ipos:', ipos, 'ifinish:', ifinish,)

        if qtoken != itokens[ipos]:
            if TRACE_EXTEND_DEEP: logger_debug('         >> NOT EQUAL in extend right')

            if (not with_gaps) or (not thresholds_max_gap_skip) or skipped > thresholds_max_gap_skip:  # or (thresholds_small and ipos - 1 not in gaps):
                if TRACE_EXTEND_DEEP:
                    if not with_gaps: logger_debug('           >>>  Not with_gap. Stop extend right')
                    if skipped > thresholds_max_gap_skip: logger_debug('           >>>  Reached max gap. Stop extend right')
                    if thresholds_small and ipos - 1 not in gaps: logger_debug('           >>>  Small: not a gap. Stop extend right')
                break

            if ipos - 1 in gaps:
                if TRACE_EXTEND_DEEP: logger_debug('           >>>  GAP continue right')
                qpos += 1
                skipped = 0
                continue

            if qtoken is None:
                if TRACE_EXTEND_DEEP: logger_debug('           >>>  None: continue right')
                qpos += 1
                skipped += 1
                continue

            if TRACE_EXTEND_DEEP: logger_debug('           >>>  No gap, continue right')
            qpos += 1
            skipped += 1
            continue

        # here qtokens[qpos] == itokens[ipos]
        if TRACE_EXTEND_DEEP: logger_debug('         >> EQUAL in extend right')
        skipped = 0
        # intersection[qtoken] and
        if qpos in low_matchables or qpos in high_matchables:
            if TRACE_EXTEND: logger_debug('          >> extend right: EXTENDING equal')
            qpositions_append(qpos)
            ipositions_append(ipos)

        qpos += 1
        ipos += 1

    return qpositions, ipositions


def match_small_old(idx, candidate, query_run, *args, **kwargs):
    """
    Return a list of LicenseMatch by matching the query sequence against the idx
    index, for a `candidate` tuple of (rid, rule, multiset intersection).
    Specialized for small rules that should be matched exactly.
    """
    rid, rule, _intersection = candidate
    if TRACE_SMALL: logger_debug(' #match_small: start ... with candidate:', rule)

    len_junk = idx.len_junk
    line_by_pos = query_run.line_by_pos
    query_run_matchables = query_run.matchables

    qtokens = query_run.tokens
    qbegin = query_run.start
    qfinish = query_run.end

    itokens = idx.tids_by_rid[rid]
    ibegin = 0
    ifinish = rule.length - 1
    ilen = rule.length
    ifirst = itokens[0]

    rule_matches = []

    # we do look for a whole itokens match

    qpos = qbegin
    while qpos <= qfinish:

        # FIXME: we should not have to convert to an array: this should be an array in the first place
        if qtokens[qpos] != ifirst:
            if TRACE_SMALL:
                logger_debug('   #match_small: skip not matchable qtoken to ifirst: qpos:', qpos)
            qpos += 1
            continue

        if qpos not in query_run_matchables:  # (qpos not in high_matchables) or (qpos not in low_matchables):
            if TRACE_SMALL:
                logger_debug('   #match_small: skip junk or not matchable qtoken: qpos:', qpos)
                logger_debug('   #match_small: skip junk or not matchable qtoken: matchables:', query_run.matchables)
            qpos += 1
            continue

        qslice = array('h', qtokens[qpos:qpos + ilen])
        if TRACE_SMALL: logger_debug(' #match_small: searching qslice:', repr(idx._tokens2text(qslice)), 'qpos:', qpos)

        if len(qslice) < ilen:
            if TRACE_SMALL: logger_debug('   #match_small: qslice too small')
            break

        if rule.identifier == 'apache-2.0_osgi.RULE' and idx._tokens2text(qslice) == 'bundle license http www apache org licenses license 2 0 txt':
            print('#######################')
            logger_debug(' #match_small: itokens:', repr(idx._tokens2text(itokens)))
            logger_debug(' #match_small: searching qslice:', repr(idx._tokens2text(qslice)), 'qpos:', qpos)
            print('#######################')
            print(qslice)
            print(itokens)
            print('#######################')

        if qslice != itokens:
            if TRACE_SMALL: logger_debug('   #match_small: skip not matched qslice')
            qpos += 1
            continue

        # here the qslice was matched:
        qspan, ispan = Span(range(qpos, qpos + ilen)), Span(ibegin, ifinish)
        hispan = Span(p for p in ispan if itokens[p] >= len_junk)

        match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, 'small')

        if TRACE_SMALL: logger_debug('   #match_small: MATCH', match)

        rule_matches.append(match)
        query_run.subtract(match.qspan)
        query_run_matchables = query_run.matchables

        if not query_run.high_matchables:
            if TRACE_SMALL: logger_debug(' #match_small: not query_run.high_matchables for qtoken:', repr(idx._tokens2text([qtokens[qpos]])), 'qpos:', qpos)
            break

        qpos += ilen + 1

    if TRACE and rule_matches:
        logger_debug('match_small: matches found#', rule_matches)

    if TRACE_SMALL:
        logger_debug('match_small: matches found#', len(rule_matches))
        if TRACE_SMALL: map(logger_debug, rule_matches)

    return rule_matches


def match_small(idx, candidate, query_run, *args, **kwargs):
    """
    Return a list of LicenseMatch by matching the query sequence against the idx
    index, for a `candidate` tuple of (rid, rule, multiset intersection).
    Specialized for small rules that should be matched exactly.
    """
    rid, rule, _intersection = candidate
    if TRACE_SMALL: logger_debug(' #match_small: start ... with candidate:', rule)

    len_junk = idx.len_junk
    line_by_pos = query_run.line_by_pos
    query_run_matchables = query_run.matchables

    qtokens = query_run.tokens
    qbegin = query_run.start

    itokens = idx.tids_by_rid[rid]
    ibegin = 0
    ifinish = rule.length - 1
    ilen = rule.length
    ifirst = itokens[0]

    rule_matches = []

    # we do look for a whole itokens match
    skip = 0
    for qpos, qtoken in enumerate(qtokens, qbegin):
        # FIXME: we should not have to convert to an array: this should be an array in the first place
        if skip:
            for _ in range(skip):
                skip -= 1
                continue

        if qtoken != ifirst:
            if TRACE_SMALL:
                logger_debug('   #match_small: skip not matchable qtoken to ifirst: qpos:', qpos, repr(idx._tokens2text([qtoken])))
            continue

        if qpos not in query_run_matchables:  # (qpos not in high_matchables) or (qpos not in low_matchables):
            if TRACE_SMALL:
                logger_debug('   #match_small: skip junk or not matchable qtoken: qpos:', qpos)
                #logger_debug('   #match_small: skip junk or not matchable qtoken: matchables:', query_run.matchables)
            continue
        qrelpos = qpos -qbegin
        qslice = array('h', qtokens[qrelpos:qrelpos + ilen])
        if TRACE_SMALL: logger_debug(' #match_small: searching qslice:', repr(idx._tokens2text(qslice)), 'qpos:', qpos)

        if len(qslice) < ilen:
            if TRACE_SMALL: logger_debug('   #match_small: qslice too small')
            break

        if qslice != itokens:
            if TRACE_SMALL: logger_debug('   #match_small: skip not matched qslice')
            qpos += 1
            continue

        skip = ilen
        # here the qslice was matched:
        qspan, ispan = Span(range(qpos, qpos + ilen)), Span(ibegin, ifinish)
        hispan = Span(p for p in ispan if itokens[p] >= len_junk)

        match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, 'small')

        if TRACE_SMALL: logger_debug('   #match_small: MATCH', match)

        rule_matches.append(match)
        query_run.subtract(match.qspan)
        query_run_matchables = query_run.matchables

        if not query_run.high_matchables:
            #if TRACE_SMALL: logger_debug(' #match_small: not query_run.high_matchables for qtoken:', repr(idx._tokens2text([qtokens[qpos]])), 'qpos:', qpos)
            break

    if TRACE and rule_matches:
        logger_debug('match_small: matches found#', rule_matches)

    if TRACE_SMALL:
        logger_debug('match_small: matches found#', len(rule_matches))
        if TRACE_SMALL: map(logger_debug, rule_matches)

    return rule_matches
